import { useEffect, useRef } from "react"

export interface FlickeringGridProps {
  squareSize?: number
  gridGap?: number
  flickerChance?: number
  color?: string
  width?: number
  height?: number
  className?: string
  maxOpacity?: number
}

export function FlickeringGrid({
  squareSize = 4,
  gridGap = 6,
  flickerChance = 0.3,
  color = "rgb(0, 0, 0)",
  width,
  height,
  className = "",
  maxOpacity = 0.2,
}: FlickeringGridProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const opacitiesRef = useRef<number[]>([])
  const rafRef = useRef<number>(0)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true
    const canvas = canvasRef.current
    if (!canvas) return

    const parent = canvas.parentElement
    const getSize = () => {
      if (width != null && height != null) return { w: width, h: height }
      const pw = parent?.clientWidth ?? 0
      const ph = parent?.clientHeight ?? 0
      return {
        w: pw || (typeof window !== "undefined" ? window.innerWidth : 800),
        h: ph || (typeof window !== "undefined" ? window.innerHeight : 600),
      }
    }

    let cols = 0
    let rows = 0
    const resize = () => {
      const { w, h } = getSize()
      canvas.width = w
      canvas.height = h
      cols = Math.ceil(w / (squareSize + gridGap)) + 1
      rows = Math.ceil(h / (squareSize + gridGap)) + 1
      const total = cols * rows
      if (opacitiesRef.current.length !== total) {
        opacitiesRef.current = Array.from({ length: total }, () => 0)
      }
    }
    resize()

    const resizeObserver =
      typeof ResizeObserver !== "undefined" && parent
        ? new ResizeObserver(resize)
        : null
    if (resizeObserver && parent) resizeObserver.observe(parent)
    if (!parent && typeof window !== "undefined") window.addEventListener("resize", resize)

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let observer: IntersectionObserver | null = null
    let isVisible = true

    const draw = () => {
      if (!mountedRef.current || !ctx || !canvas) return
      if (!isVisible) {
        rafRef.current = requestAnimationFrame(draw)
        return
      }

      const cellWidth = squareSize + gridGap
      const cellHeight = squareSize + gridGap
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
          const idx = i * cols + j
          if (Math.random() < flickerChance) {
            opacitiesRef.current[idx] = Math.random() * maxOpacity
          }
          const opacity = opacitiesRef.current[idx]
          if (opacity > 0) {
            ctx.fillStyle = color
            ctx.globalAlpha = opacity
            ctx.fillRect(
              j * cellWidth + gridGap / 2,
              i * cellHeight + gridGap / 2,
              squareSize,
              squareSize
            )
            ctx.globalAlpha = 1
          }
        }
      }

      rafRef.current = requestAnimationFrame(draw)
    }

    observer = new IntersectionObserver(
      ([entry]) => {
        isVisible = entry.isIntersecting
      },
      { threshold: 0 }
    )
    observer.observe(canvas)

    rafRef.current = requestAnimationFrame(draw)

    return () => {
      mountedRef.current = false
      cancelAnimationFrame(rafRef.current)
      observer?.disconnect()
      resizeObserver?.disconnect()
      if (typeof window !== "undefined") window.removeEventListener("resize", resize)
    }
  }, [squareSize, gridGap, flickerChance, color, width, height, maxOpacity])

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
      }}
      aria-hidden
    />
  )
}
