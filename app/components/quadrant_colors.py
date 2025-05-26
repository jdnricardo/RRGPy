QUADRANT_COLORS = {
    "Leading": "rgba(76, 175, 80, 0.3)",  # Green, 30% opacity
    "Improving": "rgba(33, 150, 243, 0.3)",  # Blue, 30% opacity
    "Weakening": "rgba(255, 235, 59, 0.3)",  # Yellow, 30% opacity
    "Lagging": "rgba(244, 67, 54, 0.3)",  # Red, 30% opacity
}

QUADRANT_COLORS_SOLID = {
    "Leading": "rgba(76, 175, 80, 1.0)",
    "Improving": "rgba(33, 150, 243, 1.0)",
    "Weakening": "rgba(255, 235, 59, 1.0)",
    "Lagging": "rgba(244, 67, 54, 1.0)",
}

QUADRANT_COLORS_SOLID_TEXT = {
    "Leading": QUADRANT_COLORS_SOLID["Leading"],
    "Improving": QUADRANT_COLORS_SOLID["Improving"],
    "Weakening": "#000000",  # Black (for contrast)
    "Lagging": QUADRANT_COLORS_SOLID["Lagging"],
}
