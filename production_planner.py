# production_planner.py
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (same dir as this file)
load_dotenv(Path(__file__).resolve().parent / ".env")

try:
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        client = Groq(api_key=api_key)
        GROQ_AVAILABLE = True
    else:
        print("⚠️ GROQ_API_KEY not found in .env file")
        GROQ_AVAILABLE = False
        client = None
except ImportError:
    print("⚠️ Groq package not installed. Install with: pip install groq")
    GROQ_AVAILABLE = False
    client = None
except Exception as e:
    print(f"⚠️ Groq client initialization failed: {e}")
    GROQ_AVAILABLE = False
    client = None

PRODUCTION_PROMPT = """You are a professional film production planner, line producer, and risk assessment expert.

TASK:
Given:
1. A movie/script text
2. A total production budget (numeric value)

Your job is to analyze the script and produce a complete production breakdown that includes:
- Scene division
- Budget allocation
- Safety requirements
- Risk identification and classification

INSTRUCTIONS:

Step 1: Scene Breakdown
- Divide the script into logical scenes. If a number of scenes is specified, create exactly that many scenes.
- Each scene must include:
  - Scene number
  - Scene title (short descriptive name)
  - Location (indoor/outdoor)
  - Time of day (day/night)
  - Brief scene description

Step 2: Budget Allocation
- Allocate the given total budget across all scenes.
- Ensure:
  - Total allocated budget = total budget provided
  - Allocation is realistic based on scene complexity
- For each scene, break budget into:
  - Cast & crew
  - Location & set
  - Props & costumes
  - Equipment & technical
  - Special effects / stunts (if any)
  - Miscellaneous

Step 3: Safety Requirements
- Identify safety measures required for each scene.
- Consider:
  - Physical safety
  - Environmental hazards
  - Equipment usage
  - Crowd management
  - Fire, water, heights, vehicles, weapons, or animals (if applicable)

Step 4: Risk Identification & Classification
- Identify potential risks for each scene.
- Classify each risk as:
  - Low
  - Medium
  - High
- For each risk, provide:
  - Risk description
  - Risk level
  - Mitigation strategy

Step 5: Budget Optimization Check
- Verify that the entire production stays within budget.
- If a scene is high-cost:
  - Suggest cost-saving alternatives without affecting story quality.

Step 6: Cast / Actor Requirements (for scheduling)
- For each scene, specify which actors are required in that scene by name.
- Use ONLY actor names from the provided list below (match spelling exactly).
- For each scene, set "required_actors": [ "ActorName1", "ActorName2" ] and "estimated_days": number (default 1).
- If no actors are provided, use empty required_actors and estimated_days: 1 for each scene.

OUTPUT FORMAT (STRICT JSON):
Return the response strictly in valid JSON using the following structure:

{
  "total_budget": number,
  "scenes": [
    {
      "scene_number": number,
      "scene_title": string,
      "location": string,
      "time_of_day": string,
      "description": string,
      "required_actors": [ "string" ],
      "estimated_days": number,
      "budget": {
        "total_scene_budget": number,
        "breakdown": {
          "cast_and_crew": number,
          "location_and_set": number,
          "props_and_costumes": number,
          "equipment_and_technical": number,
          "special_effects_and_stunts": number,
          "miscellaneous": number
        }
      },
      "safety_measures": [
        string
      ],
      "risks": [
        {
          "risk_description": string,
          "risk_level": "Low | Medium | High",
          "mitigation": string
        }
      ]
    }
  ],
  "budget_summary": {
    "total_allocated": number,
    "remaining_budget": number
  }
}

IMPORTANT RULES:
- Do NOT exceed the total budget.
- Be realistic and industry-standard.
- Do NOT include any explanation outside the JSON.
- Output must be directly usable by a software application."""

EXTRACT_ACTORS_PROMPT = """You are a script analyst. Your task is to extract the main character/actor names from a movie or film script.

RULES:
- Return ONLY the names of characters who appear as speaking or significant roles (not extras or "MAN" / "WOMAN" unless named).
- Use the exact names as they appear in the script (e.g. RAVI -> Ravi, PRIYA -> Priya).
- Return between 1 and 20 names. No duplicates.
- Do NOT include any explanation. Return ONLY a valid JSON array of strings.

Example output: ["Ravi", "Priya", "Vikram"]

Script:
"""


def extract_actor_names_from_script(script_text: str):
    """Extract character/actor names from script using Groq. Returns {"actor_names": [...]} or {"error": "..."}."""
    if not script_text or not (script_text := script_text.strip()):
        return {"actor_names": []}
    if not GROQ_AVAILABLE or not client:
        return {"error": "Groq API not available. Please add GROQ_API_KEY to your .env file."}
    # Keep extract prompt short for faster response (~5–15 sec)
    script_slice = script_text[:8000] if len(script_text) > 8000 else script_text
    try:
        prompt = f"{EXTRACT_ACTORS_PROMPT}\n{script_slice}"
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You extract character names from scripts. Reply with a JSON array of strings only, e.g. [\"Name1\", \"Name2\"]."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        names = json.loads(content)
        if not isinstance(names, list):
            return {"error": "Invalid response: expected JSON array"}
        actor_names = [str(n).strip() for n in names if n and str(n).strip()]
        return {"actor_names": actor_names}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse actor names: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


def _normalize_scenes(result, actor_names):
    """Ensure each scene has required_actors (list) and estimated_days (int >= 1)."""
    for scene in result.get("scenes", []):
        if "required_actors" not in scene:
            scene["required_actors"] = []
        if not isinstance(scene["required_actors"], list):
            scene["required_actors"] = []
        # Keep only actor names that exist in our list (normalize match)
        allowed = {n.strip() for n in actor_names} if actor_names else set()
        if allowed:
            scene["required_actors"] = [a for a in scene["required_actors"] if a and (a in allowed or a.strip() in allowed)]
        if "estimated_days" not in scene or not isinstance(scene["estimated_days"], (int, float)):
            scene["estimated_days"] = 1
        scene["estimated_days"] = max(1, int(scene["estimated_days"]))


def _actor_model(actors_list):
    """Build actor dict: name -> { daily_rate, available_days, remaining_days }."""
    model = {}
    for a in actors_list or []:
        name = (a.get("name") or "").strip()
        if not name:
            continue
        model[name] = {
            "daily_rate": float(a.get("daily_rate") or 0),
            "available_days": int(a.get("available_days") or 0),
            "remaining_days": int(a.get("available_days") or 0),
        }
    return model


def _scene_cost(scene, actor_model):
    """Sum of (actor.daily_rate * scene.estimated_days) for each required actor."""
    total = 0
    for aname in scene.get("required_actors") or []:
        if aname in actor_model:
            total += actor_model[aname]["daily_rate"] * scene.get("estimated_days", 1)
    return total


def _min_remaining_days(scene, actor_model):
    """Minimum remaining_days among required actors for this scene."""
    required = scene.get("required_actors") or []
    if not required:
        return float("inf")
    mins = []
    for aname in required:
        if aname in actor_model:
            mins.append(actor_model[aname]["remaining_days"])
    return min(mins) if mins else 0


def _apply_user_scene_assignments(result, actors_list):
    """Override each scene's required_actors from user-provided scene_numbers (actor present in which scenes)."""
    if not actors_list:
        return
    for scene in result.get("scenes", []):
        sn = scene.get("scene_number")
        if sn is None:
            continue
        required = []
        for a in actors_list:
            name = (a.get("name") or "").strip()
            if not name:
                continue
            scene_nums = a.get("scene_numbers") or []
            if sn in scene_nums or int(sn) in scene_nums:
                required.append(name)
        scene["required_actors"] = required


def _build_calendar_and_blocked(result, actors_list):
    """Python-only scheduling: sort scenes, build shooting_calendar, blocked_scenes, suggestions."""
    if not actors_list:
        result["shooting_calendar"] = []
        result["blocked_scenes"] = []
        result["suggestions"] = []
        return

    # If actors have scene_numbers, override required_actors per scene from user input
    if any((a.get("scene_numbers") or []) for a in actors_list):
        _apply_user_scene_assignments(result, actors_list)

    actor_model = _actor_model(actors_list)
    actor_names = list(actor_model.keys())
    _normalize_scenes(result, actor_names)

    scenes = list(result.get("scenes", []))
    # Working copy of actor remaining_days (we mutate during calendar build)
    remaining = {name: data["remaining_days"] for name, data in actor_model.items()}

    def sort_key(scene):
        min_rem = float("inf")
        for aname in scene.get("required_actors") or []:
            if aname in remaining:
                min_rem = min(min_rem, remaining[aname])
        cost = _scene_cost(scene, actor_model)
        return (min_rem, -cost)

    sorted_scenes = sorted(scenes, key=sort_key)

    shooting_calendar = []
    blocked_scenes = []
    current_day = 1

    for scene in sorted_scenes:
        sn = scene.get("scene_number")
        req_actors = scene.get("required_actors") or []
        est_days = scene.get("estimated_days", 1)

        shortage_actor = None
        days_missing = 0
        if req_actors:
            for aname in req_actors:
                if aname not in remaining:
                    continue
                if remaining[aname] < est_days:
                    need = est_days - remaining[aname]
                    if need > days_missing:
                        days_missing = need
                        shortage_actor = aname

        can_schedule = not req_actors or (req_actors and all(remaining.get(a, 0) >= est_days for a in req_actors))

        if can_schedule:
            start_day = current_day
            end_day = current_day + est_days - 1
            shooting_calendar.append({
                "scene_number": sn,
                "start_day": start_day,
                "end_day": end_day,
                "actors": req_actors,
            })
            for aname in req_actors:
                if aname in remaining:
                    remaining[aname] -= est_days
            current_day = end_day + 1
        else:
            reason = f"Actor '{shortage_actor or req_actors[0]}' needs {days_missing or est_days} more day(s)"
            blocked_scenes.append({
                "scene_number": sn,
                "reason": reason,
                "actor_shortage": shortage_actor or (req_actors[0] if req_actors else None),
                "days_missing": days_missing or est_days,
            })

    result["shooting_calendar"] = shooting_calendar
    result["blocked_scenes"] = blocked_scenes

    suggestions = []
    for b in blocked_scenes:
        actor_short = b.get("actor_shortage")
        days_m = b.get("days_missing")
        if actor_short and days_m:
            suggestions.append(f"Increase {actor_short} availability by {days_m} day(s)")
    if blocked_scenes and len(blocked_scenes) >= 2:
        suggestions.append("Increase budget or reduce scene count to ease scheduling")
    high_cost_scenes = [s for s in scenes if _scene_cost(s, actor_model) > 0 and len(s.get("required_actors") or []) >= 2]
    if high_cost_scenes:
        suggestions.append("Consider replacing a supporting actor to reduce cost on high-cost scenes")
    result["suggestions"] = suggestions


# Limit script length sent to LLM to avoid huge prompts and slow timeouts (Groq has context limits)
MAX_SCRIPT_CHARS = 12000

def generate_production_plan(script_text: str, total_budget: float, actors=None, number_of_scenes=None):
    """Generate production breakdown using Groq; then run Python scheduling if actors provided."""
    
    if not GROQ_AVAILABLE or not client:
        return {
            "error": "Groq API not available. Please add GROQ_API_KEY to your .env file."
        }
    
    actors_list = actors if isinstance(actors, list) else []
    actor_names_str = ""
    if actors_list:
        names = [str(a.get("name", "")).strip() for a in actors_list if a.get("name")]
        if names:
            actor_names_str = "\n\nAvailable actors (use these exact names in required_actors): " + ", ".join(names)

    scene_count_str = ""
    if number_of_scenes is not None and number_of_scenes > 0:
        scene_count_str = f"\n\nCreate exactly {int(number_of_scenes)} scenes in the scene breakdown."

    # Truncate long scripts so the API call stays fast (full script can cause 60s+ delays)
    script_for_prompt = (script_text or "").strip()
    if len(script_for_prompt) > MAX_SCRIPT_CHARS:
        script_for_prompt = script_for_prompt[:MAX_SCRIPT_CHARS] + "\n\n[... script truncated for speed ...]"

    try:
        prompt = f"{PRODUCTION_PROMPT}\n\nScript:\n{script_for_prompt}\n\nTotal Budget: ₹{total_budget:,.2f} (Indian Rupees){scene_count_str}{actor_names_str}"
        
        # Default 70B model is accurate but slower; set GROQ_MODEL=llama-3.1-8b-instant in .env for faster (30b also available)
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional film production planner. Always return valid JSON only, no explanations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to extract JSON if wrapped in markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        result = json.loads(content)
        
        # Validate structure
        if "scenes" not in result or "total_budget" not in result:
            return {"error": "Invalid response format from AI"}
        
        # Python-only scheduling (actor availability, calendar, blocked, suggestions)
        _build_calendar_and_blocked(result, actors_list)
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON decode error: {e}")
        print(f"Response content: {content[:500]}")
        return {"error": f"Failed to parse AI response as JSON: {str(e)}"}
    except Exception as e:
        print(f"⚠️ Error generating production plan: {e}")
        return {"error": f"Error generating production plan: {str(e)}"}

