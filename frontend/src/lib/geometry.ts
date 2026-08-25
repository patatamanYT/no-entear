/** Geometry helpers: convex hull (monotone chain) + polygon area (shoelace). */

export interface Pt {
  x: number;
  y: number;
}

function cross(o: Pt, a: Pt, b: Pt): number {
  return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
}

/**
 * Andrew's monotone chain convex hull. Returns hull points in CCW order,
 * starting/ending distinct (no repeated first point). Returns the input
 * (deduped) unchanged if fewer than 3 distinct points remain.
 */
export function convexHull(points: Pt[]): Pt[] {
  const pts = Array.from(
    new Map(points.map((p) => [`${p.x.toFixed(6)},${p.y.toFixed(6)}`, p])).values(),
  ).sort((a, b) => (a.x === b.x ? a.y - b.y : a.x - b.x));

  if (pts.length < 3) return pts;

  const lower: Pt[] = [];
  for (const p of pts) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) {
      lower.pop();
    }
    lower.push(p);
  }

  const upper: Pt[] = [];
  for (let i = pts.length - 1; i >= 0; i--) {
    const p = pts[i];
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) {
      upper.pop();
    }
    upper.push(p);
  }

  lower.pop();
  upper.pop();
  return lower.concat(upper);
}

/** Shoelace formula. Assumes a simple (non-self-intersecting) polygon. */
export function polygonArea(points: Pt[]): number {
  if (points.length < 3) return 0;
  let area = 0;
  for (let i = 0; i < points.length; i++) {
    const a = points[i];
    const b = points[(i + 1) % points.length];
    area += a.x * b.y - b.x * a.y;
  }
  return Math.abs(area) / 2;
}

/** Convenience: convex hull area of a point set, in the same units as input (m^2 for pitch meters). */
export function hullArea(points: Pt[]): number {
  return polygonArea(convexHull(points));
}
