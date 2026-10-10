// risk-utils.js
// Extracted pure geometry and scoring functions from frontend/index.html
// Compatible with both browser (pt objects with lat/lng) and Node.js (synthetic coords)
// Uses the same planar approximation as the original frontend code

/**
 * Convert a point to local Cartesian coordinates (meters from equator origin).
 * Same conversion as in frontend/index.html segmentToSegmentDist:
 *   x = lng * 111320 * cos(lat_rad)
 *   y = lat * 110540
 * Planar approximation suitable for regional routes.
 */
function ptToLocal(pt) {
  const latRad = pt.lat * Math.PI / 180;
  return { x: pt.lng * 111320 * Math.cos(latRad), y: pt.lat * 110540 };
}

/**
 * Calculate the distance between two line segments in meters.
 * segmentToSegmentDist(p1, p2, p3, p4)
 * - p1, p2: line segment 1 (each point has {lat, lng})
 * - p3, p4: line segment 2 (each point has {lat, lng})
 * Returns the shortest distance between the two segments in meters.
 * Uses a robust 2D segment-distance algorithm with explicit intersection
 * detection and proper handling of degenerate cases.
 * Planar approximation suitable for regional routes.
 */
function segmentToSegmentDist(p1, p2, p3, p4) {
  // Project all four geographic points into one shared local coordinate system
  const A = ptToLocal(p1), B = ptToLocal(p2);
  const C = ptToLocal(p3), D = ptToLocal(p4);

  // Vector AB and CD
  const ABx = B.x - A.x, ABy = B.y - A.y;
  const CDx = D.x - C.x, CDy = D.y - C.y;

  // Check if segments degenerate to points
  const ABlen2 = ABx * ABx + ABy * ABy;
  const CDlen2 = CDx * CDx + CDy * CDy;

  // If both segments are points
  if (ABlen2 === 0 && CDlen2 === 0) {
    return Math.hypot(A.x - C.x, A.y - C.y);
  }

  // If first segment is a point, find its distance to segment CD
  if (ABlen2 === 0) {
    return pointToSegmentDist(A, C, D);
  }

  // If second segment is a point, find its distance to segment AB
  if (CDlen2 === 0) {
    return pointToSegmentDist(C, A, B);
  }

  // Compute closest points on the infinite lines AB and CD
  const ACx = C.x - A.x, ACy = A.y - C.y;
  const BCx = B.x - C.x, BCy = B.y - C.y;
  const denominator = ABx * CDy - ABy * CDx;

  // Parallel case: denominator near zero
  if (Math.abs(denominator) < 1e-12) {
    // Segments are parallel; minimum of the four endpoint-to-segment distances
    return Math.min(
      pointToSegmentDist(A, C, D),
      pointToSegmentDist(B, C, D),
      pointToSegmentDist(C, A, B),
      pointToSegmentDist(D, A, B)
    );
  }

  // General case: closest points on the infinite lines
  let s = ((ACx * CDy - ACy * CDx) / denominator);
  let t = ((ACx * ABy - ACy * ABx) / denominator);

  // Check if closest points fall within both segments
  const sInRange = s >= 0 && s <= 1;
  const tInRange = t >= 0 && t <= 1;

  if (sInRange && tInRange) {
    // Closest points are within both segments — return their distance
    const closestA = { x: A.x + s * ABx, y: A.y + s * ABy };
    const closestC = { x: C.x + t * CDx, y: C.y + t * CDy };
    return Math.hypot(closestA.x - closestC.x, closestA.y - closestC.y);
  }

  // Closest points on the infinite lines fall outside the segments.
  // Return the minimum of the four endpoint-to-segment distances.
  return Math.min(
    pointToSegmentDist(A, C, D),
    pointToSegmentDist(B, C, D),
    pointToSegmentDist(C, A, B),
    pointToSegmentDist(D, A, B)
  );
}

/**
 * Calculate the distance from a point to a line segment in meters.
 * pointToSegmentDist(p, a, b)
 * - p: the point
 * - a, b: the segment endpoints
 * Returns the shortest distance from the point to the segment.
 */
function pointToSegmentDist(p, a, b) {
  const ABx = b.x - a.x, ABy = b.y - a.y;
  const APx = p.x - a.x, APy = p.y - a.y;
  const ABlen2 = ABx * ABx + ABy * ABy;

  // If the segment is a point
  if (ABlen2 === 0) {
    return Math.hypot(p.x - a.x, p.y - a.y);
  }

  // Project the point onto the infinite line, then clamp to the segment
  let t = (APx * ABx + APy * ABy) / ABlen2;
  t = Math.max(0, Math.min(1, t));

  // The projected point on the segment
  const proj = { x: a.x + t * ABx, y: a.y + t * ABy };
  return Math.hypot(p.x - proj.x, p.y - proj.y);
}

/**
 * Calculate the distance between two line segments in meters.
 * segmentToSegmentDist(p1, p2, p3, p4)
 * Uses the same planar approximation as the rest of the module.
 * See segmentToSegmentDist above for full details.
 * @deprecated Use segmentToSegmentDist instead.
 * @private
 */
function _legacySegmentToSegmentDist(p1, p2, p3, p4) {
  const A = ptToLocal(p1), B = ptToLocal(p2);
  const C = ptToLocal(p3), D = ptToLocal(p4);

  const ABx = B.x - A.x, ABy = B.y - A.y;
  const CDx = D.x - C.x, CDy = D.y - C.y;

  const ABlen2 = ABx * ABx + ABy * ABy;
  const CDlen2 = CDx * CDx + CDy * CDy;

  if (ABlen2 === 0 && CDlen2 === 0) {
    return Math.hypot(A.x - C.x, A.y - C.y);
  }
  if (ABlen2 === 0) {
    const t = ((C.x - A.x) * CDx + (C.y - A.y) * CDy) / CDlen2;
    const tClamped = Math.max(0, Math.min(1, t));
    const proj = { x: C.x + tClamped * CDx, y: C.y + tClamped * CDy };
    return Math.hypot(A.x - proj.x, A.y - proj.y);
  }
  if (CDlen2 === 0) {
    const t = ((A.x - C.x) * ABx + (A.y - C.y) * ABy) / ABlen2;
    const tClamped = Math.max(0, Math.min(1, t));
    const proj = { x: A.x + tClamped * ABx, y: A.y + tClamped * ABy };
    return Math.hypot(C.x - proj.x, C.y - proj.y);
  }

  const ACx = C.x - A.x, ACy = A.y - C.y;
  const ADx = D.x - A.x, ADy = D.y - A.y;
  const BCx = B.x - C.x, BCy = B.y - C.y;
  const denominator = ABx * CDy - ABy * CDx;

  let s = 0, t = 0;
  if (Math.abs(denominator) > 1e-6) {
    s = ((ACx * CDy - ACy * CDx) / denominator);
    t = ((ACx * ABy - ACy * ABx) / denominator);
  }

  const sClamped = Math.max(0, Math.min(1, s));
  const tClamped = Math.max(0, Math.min(1, t));

  const closestA = { x: A.x + sClamped * ABx, y: A.y + sClamped * ABy };
  const closestC = { x: C.x + tClamped * CDx, y: C.y + tClamped * CDy };

  const dx = closestA.x - closestC.x;
  const dy = closestA.y - closestC.y;
  return Math.hypot(dx, dy);
}


/**
 * Compute the route risk score using the same formula as frontend/index.html.
 * score = HIGH_RISK_hits * 100 + MONITOR_hits * 10 + duration_minutes / 1000
 * @param {object} route - { hits: [{lvl}], mins: number }
 * @returns {number} score (lower is better)
 */
function computeRouteScore(route) {
  return route.hits.filter(h => h.lvl === "HIGH_RISK").length * 100 +
         route.hits.filter(h => h.lvl === "MONITOR").length * 10 +
         route.mins / 1000;
}

/**
 * Select the best route (lowest score) from an array of routes.
 * Same logic as frontend/index.html:
 *   const best = routes.reduce((bi, x, i) => score(x) < score(routes[bi]) ? i : bi, 0);
 * @param {Array} routes - array of { hits: [{lvl}], mins: number }
 * @returns {number} index of the best route
 */
function selectBestRoute(routes) {
  return routes.reduce((bi, x, i) => computeRouteScore(x) < computeRouteScore(routes[bi]) ? i : bi, 0);
}

/**
 * Filter risky roads along a route using segment-based distance detection.
 * Same logic as the route processing in frontend/index.html.
 * @param {Array} path - array of {lat, lng} waypoints
 * @param {Array} risky - array of {r: roadId, lvl: "HIGH_RISK"|"MONITOR"|...}
 * @param {Array} roads - array of {id, path: [{lat,lng}, ...]}
 * @param {number} threshold_m - proximity threshold in meters (default: 150)
 * @returns {Array} filtered hits with {r, lvl}
 */
function findRouteRiskHits(path, risky, roads, threshold_m = 150) {
  const hits = risky.filter(({ r }) => {
    const road = roads.find(road => r.r === road.id);
    if (!road) return false;
    const roadPath = road.path;
    let minDist = Infinity;

    // Check distance from each route segment to each road segment
    for (let i = 0; i < path.length - 1; i++) {
      const p1 = path[i];
      const p2 = path[i + 1];
      for (let j = 0; j < roadPath.length - 1; j++) {
        const r1 = roadPath[j];
        const r2 = roadPath[j + 1];
        minDist = Math.min(minDist, segmentToSegmentDist(p1, p2, r1, r2));
      }
    }
    // Also check vertices against road
    for (const p of path) {
      minDist = Math.min(minDist, pointToRoadDist(p, road));
    }
    return minDist < threshold_m;
  });

  return hits;
}

/**
 * Calculate distance from a point to a road line segment.
 * Used as a fallback in findRouteRiskHits.
 */
function pointToRoadDist(point, road) {
  const roadPath = road.path;
  let minDist = Infinity;
  for (let i = 0; i < roadPath.length - 1; i++) {
    minDist = Math.min(minDist, segmentToSegmentDist(point, point, roadPath[i], roadPath[i + 1]));
  }
  return minDist;
}

// Export for Node.js and browser compatibility
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    segmentToSegmentDist,
    computeRouteScore,
    selectBestRoute,
    findRouteRiskHits,
    pointToRoadDist
  };
} else {
  // Browser global (will be available if loaded as a script tag)
  window.riskUtils = {
    segmentToSegmentDist,
    computeRouteScore,
    selectBestRoute,
    findRouteRiskHits,
    pointToRoadDist
  };
}