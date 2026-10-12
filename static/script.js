// Wait for the HTML document to be fully loaded before running script
document.addEventListener('DOMContentLoaded', () => {
  // Check if the user has enabled reduced motion in their OS or browser settings
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Select the signpost arrows SVG group element by its ID
  const signpostArrows = document.getElementById('signpost-arrows');

  // If the element exists and reduced motion is not requested, trigger the wobble
  if (signpostArrows && !prefersReducedMotion) {
    // Adding the class activates the single CSS wobble keyframe animation
    signpostArrows.classList.add('wobble-arrows');
  }
});
