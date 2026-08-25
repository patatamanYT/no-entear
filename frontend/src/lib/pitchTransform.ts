/**
 * Coordinate transform between pitch-meter space (0..60 x, 0..40 y, origin
 * bottom-left / top-left depending on consumer) and SVG viewBox space.
 *
 * We render the pitch in an SVG with viewBox "0 0 W H" where W:H == 60:40
 * (fútbol 7).
 * Pitch meters map 1:1 onto viewBox units, so the transform is a simple
 * identity + optional Y-flip. We keep Y not flipped (SVG y grows downward,
 * same as row-major heatmap data where row 0 = y near 0) so heatmap rows and
 * pitch y both increase "down" the viewBox consistently.
 */

import { PITCH_LENGTH_M, PITCH_WIDTH_M } from "@/types/match";

export const PITCH_VB_WIDTH = PITCH_LENGTH_M;
export const PITCH_VB_HEIGHT = PITCH_WIDTH_M;

export interface PitchTransform {
  /** Convert a pitch-meter point to SVG viewBox units. */
  toSvg: (x: number, y: number) => { x: number; y: number };
  /** Convert an SVG viewBox point back to pitch meters. */
  toPitch: (x: number, y: number) => { x: number; y: number };
  viewBox: string;
  width: number;
  height: number;
}

/**
 * Pitch meters map 1:1 to viewBox units. Consumers scale the <svg> element
 * itself (via CSS width/height / preserveAspectRatio) to fit the container.
 */
export function createPitchTransform(): PitchTransform {
  return {
    toSvg: (x, y) => ({ x, y }),
    toPitch: (x, y) => ({ x, y }),
    viewBox: `0 0 ${PITCH_VB_WIDTH} ${PITCH_VB_HEIGHT}`,
    width: PITCH_VB_WIDTH,
    height: PITCH_VB_HEIGHT,
  };
}
