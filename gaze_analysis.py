"""
Gaze Analysis Module for Camera Position Awareness
===================================================

Detects:
1. Where user is looking (camera vs screen)
2. Eye conditions (lazy eye, strabismus, accommodation issues)
3. Accounts for camera position on top of display

Camera Position Assumptions:
- Laptop camera at TOP of display (typical position)
- Screen below camera
- User's normal gaze at screen is DOWNWARD from camera's perspective
"""

import numpy as np
from typing import Dict, Optional, Tuple


class GazeAnalyzer:
    """Analyze gaze direction and screen visibility."""
    
    def __init__(self, camera_position='top', screen_height_px=1080, screen_width_px=1920):
        """
        Initialize gaze analyzer.
        
        Args:
            camera_position: 'top', 'center', or 'bottom' relative to display
            screen_height_px: Screen height in pixels (for reference)
            screen_width_px: Screen width in pixels (for reference)
        """
        self.camera_position = camera_position
        self.screen_height = screen_height_px
        self.screen_width = screen_width_px
        
    def analyze_gaze(
        self,
        left_gaze_x: float,
        right_gaze_x: float,
        left_ear: float,
        right_ear: float,
        left_iris_y: Optional[float] = None,
        right_iris_y: Optional[float] = None,
        image_height: Optional[float] = None
    ) -> Dict:
        """
        Analyze gaze direction and determine if user is looking at screen or camera.
        
        Args:
            left_gaze_x: Horizontal gaze ratio for left eye (0=inner/nose, 1=outer/temple)
            right_gaze_x: Horizontal gaze ratio for right eye
            left_ear: Eye Aspect Ratio for left eye (blink detection)
            right_ear: Eye Aspect Ratio for right eye
            left_iris_y: Y position of left iris in image (0=top, 1=bottom)
            right_iris_y: Y position of right iris in image
            image_height: Image height in pixels (for converting normalized coords)
            
        Returns:
            Dict with:
            - 'looking_at_screen': bool (True if user eyes point downward)
            - 'looking_at_camera': bool (True if user eyes point toward camera)
            - 'gaze_direction': str ('down_at_screen', 'straight', 'up_at_camera', 'unclear')
            - 'horizontal_alignment': str ('centered', 'left_deviated', 'right_deviated')
            - 'eye_openness': str ('normal', 'partially_closed', 'closed/blinking')
            - 'accommodation_state': str ('normal', 'strain', 'relaxed')
            - 'confidence': float (0-1, confidence in analysis)
            - 'screen_visibility_ratio': float (0-1, estimate of how well user sees screen)
            - 'eye_condition_notes': str (additional observations)
        """
        
        # 1. Check eye openness (EAR)
        avg_ear = (left_ear + right_ear) / 2.0
        eye_openness, ear_confidence = self._classify_eye_openness(avg_ear)
        
        # 2. Check horizontal alignment (cross-eye tendency)
        horiz_align = self._analyze_horizontal_alignment(left_gaze_x, right_gaze_x)
        
        # 3. Determine vertical gaze direction (camera vs screen)
        gaze_direction = 'unclear'
        looking_at_screen = False
        looking_at_camera = False
        vertical_confidence = 0.5
        
        if left_iris_y is not None and right_iris_y is not None:
            # User's iris position tells us where they're looking vertically
            gaze_direction, looking_at_screen, looking_at_camera, vertical_confidence = \
                self._analyze_vertical_gaze(left_iris_y, right_iris_y, image_height)
        
        # 4. Calculate screen visibility (how much of screen can user see at this gaze)
        screen_visibility = self._calculate_screen_visibility(
            left_iris_y, right_iris_y, looking_at_screen, image_height
        )
        
        # 5. Check for accommodation strain (iris dilation, convergence issues)
        accommodation_state = self._assess_accommodation(
            left_gaze_x, right_gaze_x, left_ear, right_ear
        )
        
        # 6. Generate detailed notes about eye condition
        condition_notes = self._generate_condition_notes(
            horiz_align, eye_openness, gaze_direction, accommodation_state
        )
        
        # Overall confidence
        overall_confidence = min(
            ear_confidence * 0.3 +
            vertical_confidence * 0.4 +
            (1.0 if horiz_align != 'unclear' else 0.6) * 0.3
        , 1.0)
        
        return {
            'looking_at_screen': looking_at_screen,
            'looking_at_camera': looking_at_camera,
            'gaze_direction': gaze_direction,
            'horizontal_alignment': horiz_align,
            'eye_openness': eye_openness,
            'accommodation_state': accommodation_state,
            'confidence': float(overall_confidence),
            'screen_visibility_ratio': float(screen_visibility),
            'eye_condition_notes': condition_notes,
            'vertical_confidence': float(vertical_confidence),
            'ear_confidence': float(ear_confidence),
        }
    
    def _classify_eye_openness(self, avg_ear: float) -> Tuple[str, float]:
        """
        Classify eye openness from Eye Aspect Ratio.
        
        EAR < 0.15: Closed/Blinking
        0.15 - 0.25: Partially closed
        > 0.25: Normal/Open
        """
        if avg_ear < 0.15:
            return 'closed/blinking', 0.9
        elif avg_ear < 0.25:
            return 'partially_closed', 0.85
        else:
            return 'normal', 0.95
    
    def _analyze_horizontal_alignment(self, left_gaze_x: float, right_gaze_x: float) -> str:
        """
        Analyze horizontal eye alignment using gaze ratio asymmetry.
        
        If left_gaze_x and right_gaze_x differ significantly, indicates:
        - Esotropia (both eyes turning inward)
        - Exotropia (both eyes turning outward)
        - Strabismus (one eye misaligned)
        """
        # Expected range: 0 (inner/nose) to 1 (outer/temple)
        # Normal: ~0.4-0.6 (centered in eye)
        
        left_centered = abs(left_gaze_x - 0.5)
        right_centered = abs(right_gaze_x - 0.5)
        asymmetry = abs(left_gaze_x - right_gaze_x)
        
        if asymmetry > 0.15:  # Significant difference between eyes
            if left_gaze_x < 0.4 and right_gaze_x < 0.4:
                # Both eyes turned inward (toward nose)
                return 'both_inward_esotropia'
            elif left_gaze_x > 0.6 and right_gaze_x > 0.6:
                # Both eyes turned outward
                return 'both_outward_exotropia'
            else:
                # One eye misaligned relative to other
                return 'asymmetric_strabismus'
        elif left_centered > 0.15 or right_centered > 0.15:
            if left_gaze_x > 0.6 or right_gaze_x > 0.6:
                return 'right_deviated'
            else:
                return 'left_deviated'
        else:
            return 'centered'
    
    def _analyze_vertical_gaze(
        self,
        left_iris_y: float,
        right_iris_y: float,
        image_height: Optional[float]
    ) -> Tuple[str, bool, bool, float]:
        """
        Determine vertical gaze direction (up toward camera vs down at screen).
        
        Iris position in image:
        - Y near 0.0 (top) = eyes looking up
        - Y near 0.5 (middle) = eyes looking straight
        - Y near 1.0 (bottom) = eyes looking down
        
        For top-mounted camera:
        - User looking DOWN = looking at screen (good)
        - User looking STRAIGHT = borderline
        - User looking UP = looking at camera
        """
        avg_iris_y = (left_iris_y + right_iris_y) / 2.0
        asymmetry = abs(left_iris_y - right_iris_y)
        
        looking_at_screen = False
        looking_at_camera = False
        confidence = 0.7
        
        if asymmetry > 0.1:
            # Eyes looking in different vertical directions (may indicate strabismus)
            confidence = 0.5
            direction = 'unclear'
        elif avg_iris_y < 0.35:
            # Iris in upper half of eye = looking UP toward camera
            direction = 'up_at_camera'
            looking_at_camera = True
            confidence = 0.85
        elif avg_iris_y > 0.65:
            # Iris in lower half of eye = looking DOWN at screen
            direction = 'down_at_screen'
            looking_at_screen = True
            confidence = 0.85
        else:
            # Iris centered = looking roughly straight
            direction = 'straight'
            confidence = 0.8
        
        return direction, looking_at_screen, looking_at_camera, confidence
    
    def _calculate_screen_visibility(
        self,
        left_iris_y: Optional[float],
        right_iris_y: Optional[float],
        looking_at_screen: bool,
        image_height: Optional[float]
    ) -> float:
        """
        Estimate what portion of screen user can see based on gaze.
        
        Returns:
        - 1.0: Perfect view of screen (eyes looking directly at it)
        - 0.5: Partial view (head tilted or looking at edge)
        - 0.0: Not looking at screen (looking away or up at camera)
        """
        if not looking_at_screen:
            return 0.0
        
        if left_iris_y is not None and right_iris_y is not None:
            avg_iris_y = (left_iris_y + right_iris_y) / 2.0
            # As iris moves more to bottom of eye, viewing angle improves
            # iris_y = 0.65-0.95 = good view; iris_y = 0.50-0.65 = okay view
            if avg_iris_y > 0.75:
                return 0.95  # Excellent view
            elif avg_iris_y > 0.65:
                return 0.8   # Good view
            elif avg_iris_y > 0.55:
                return 0.6   # Moderate view
            else:
                return 0.4   # Poor view
        
        return 1.0 if looking_at_screen else 0.0
    
    def _assess_accommodation(
        self,
        left_gaze_x: float,
        right_gaze_x: float,
        left_ear: float,
        right_ear: float
    ) -> str:
        """
        Assess accommodation state (strain from focusing at screen distance).
        
        Indicators:
        - Squinting (low EAR) + centered gaze = strain
        - Sustained convergence (gaze_x extreme) = strain
        - Normal EAR + normal gaze = relaxed
        """
        avg_ear = (left_ear + right_ear) / 2.0
        avg_gaze_x = (left_gaze_x + right_gaze_x) / 2.0
        
        # Check for strain indicators
        is_squinting = avg_ear < 0.25
        is_converged = abs(avg_gaze_x - 0.5) > 0.2  # Eyes turned inward
        
        if is_squinting and is_converged:
            return 'strain'  # Both signs of strain
        elif is_squinting or is_converged:
            return 'mild_strain'
        else:
            return 'normal'
    
    def _generate_condition_notes(
        self,
        horiz_align: str,
        eye_openness: str,
        gaze_direction: str,
        accommodation_state: str
    ) -> str:
        """Generate human-readable observations about eye condition."""
        notes = []
        
        if horiz_align != 'centered':
            if 'esotropia' in horiz_align:
                notes.append("⚠️ Esotropia detected (eyes turning inward)")
            elif 'exotropia' in horiz_align:
                notes.append("⚠️ Exotropia detected (eyes turning outward)")
            elif 'strabismus' in horiz_align:
                notes.append("⚠️ Eye misalignment detected (strabismus)")
            elif 'deviated' in horiz_align:
                notes.append(f"⚠️ Horizontal deviation detected ({horiz_align})")
        
        if eye_openness == 'closed/blinking':
            notes.append("🔆 Eyes closed or blinking")
        elif eye_openness == 'partially_closed':
            notes.append("⚠️ Eyes partially closed (may indicate fatigue)")
        
        if gaze_direction == 'down_at_screen':
            notes.append("✓ User looking at screen")
        elif gaze_direction == 'up_at_camera':
            notes.append("→ User looking at camera/up")
        elif gaze_direction == 'straight':
            notes.append("→ User looking straight ahead")
        
        if accommodation_state == 'strain':
            notes.append("⚠️ Eye strain detected (squinting + convergence)")
        elif accommodation_state == 'mild_strain':
            notes.append("⚠️ Possible eye strain (fatigue)")
        
        return " | ".join(notes) if notes else "✓ Eyes in normal state"


def enhance_lazy_eye_detection(
    raw_label: str,
    confidence: float,
    left_gaze_x: float,
    right_gaze_x: float,
    left_ear: float,
    right_ear: float,
    ipd_px: float,
    left_iris_y: Optional[float] = None,
    right_iris_y: Optional[float] = None,
    image_height: Optional[float] = None
) -> Dict:
    """
    Enhanced lazy eye detection accounting for gaze direction and eye position.
    
    Returns:
    - refined_label: Better classification considering all factors
    - refined_confidence: Adjusted confidence
    - analysis: Full gaze analysis
    - diagnostics: Additional diagnostic info
    """
    analyzer = GazeAnalyzer(camera_position='top')
    
    analysis = analyzer.analyze_gaze(
        left_gaze_x, right_gaze_x, left_ear, right_ear,
        left_iris_y, right_iris_y, image_height
    )
    
    # Refine lazy eye detection
    refined_label = raw_label
    confidence_adjustment = 0.0
    diagnostics = []
    
    # If model said lazy_eye but eyes are looking at camera (up), adjust
    if raw_label == 'lazy_eye' and analysis['looking_at_camera']:
        diagnostics.append("Model detected lazy_eye but user looking at camera - may be false positive")
        confidence_adjustment = -0.15
    
    # If eyes show significant asymmetry in vertical direction
    if left_iris_y is not None and right_iris_y is not None:
        iris_y_diff = abs(left_iris_y - right_iris_y)
        if iris_y_diff > 0.15 and raw_label == 'lazy_eye':
            diagnostics.append(f"Significant vertical eye misalignment (diff={iris_y_diff:.3f}) - consistent with lazy eye")
            confidence_adjustment = +0.1
        elif iris_y_diff > 0.15:
            diagnostics.append(f"Vertical strabismus detected - review for lazy eye")
            refined_label = 'possible_lazy_eye'
            confidence_adjustment = +0.2
    
    # Eye openness check
    if analysis['eye_openness'] == 'closed/blinking':
        diagnostics.append("Eyes blinking/closed - result unreliable")
        confidence_adjustment = -0.2
    elif analysis['eye_openness'] == 'partially_closed':
        diagnostics.append("Eyes partially closed - may affect accuracy")
        confidence_adjustment = -0.1
    
    # Accommodation state
    if analysis['accommodation_state'] == 'strain':
        diagnostics.append("Eye strain detected - may affect diagnosis")
        confidence_adjustment = -0.05
    
    # Refine confidence
    refined_confidence = max(0.0, min(1.0, confidence + confidence_adjustment))
    
    return {
        'refined_label': refined_label,
        'refined_confidence': float(refined_confidence),
        'analysis': analysis,
        'diagnostics': diagnostics,
        'model_vs_refined_agreement': raw_label.lower() == refined_label.lower(),
    }
