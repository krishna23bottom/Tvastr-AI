"""Filmmaking knowledge layer.
Used in two ways:
  1. As grounding notes injected into the LLM prompt (so answers stay on-topic).
  2. As the offline fallback reply when no API key / the API is down.
"""

KNOWLEDGE = {
    "concept_development": {
        "title": "Concept Development",
        "tips": [
            "Start with ONE emotion or question (loneliness, ambition, regret) and let every image serve it.",
            "Limit the world: one location, one or two characters, one clear change from start to end.",
            "Turn the theme into a visual motif you can repeat (a window, a color, a reflection).",
            "Write the idea as one sentence: 'A [character] wants [goal] but [obstacle], so [action].'",
        ],
        "follow_up": "What emotion do you want the audience to walk away with?",
    },
    "shot_ideas": {
        "title": "Shot Ideas",
        "tips": [
            "Cover the basics first: wide establishing, medium for action, close-up for emotion, insert for detail.",
            "Use foreground elements (glass, leaves, doorframes) to add depth to simple setups.",
            "Try reflections: mirrors, car windows, puddles, sunglasses.",
            "Add one 'signature' shot: a low-angle push-in, an overhead, or a slow orbit.",
        ],
        "follow_up": "What is the location and what props do you have?",
    },
    "camera_angles": {
        "title": "Camera Angles",
        "tips": [
            "Low angle makes a subject look powerful or intimidating; high angle makes them look small or vulnerable.",
            "Eye level feels neutral and honest; use it for natural dialogue.",
            "Dutch (tilted) angle signals unease. Use it sparingly.",
            "Over-the-shoulder and POV shots build connection between characters.",
        ],
        "follow_up": "What should the viewer feel about this character in the scene?",
    },
    "camera_movement": {
        "title": "Camera Movement",
        "tips": [
            "Push-in builds tension or intimacy; pull-out reveals context or isolation.",
            "Tracking/dolly shots follow action smoothly; handheld adds urgency and realism.",
            "Pan and tilt reveal space; whip pans work as energetic transitions.",
            "Every move needs a reason. If the emotion does not change, keep the camera still.",
        ],
        "follow_up": "Do you have a gimbal, slider or tripod only?",
    },
    "composition": {
        "title": "Composition",
        "tips": [
            "Rule of thirds: place eyes or key subjects on the grid lines or intersections.",
            "Use negative space to show isolation; use symmetry for control or unease.",
            "Leading lines (roads, fences, corridors) pull the eye to the subject.",
            "Frame within a frame (doors, windows) adds depth. Watch headroom and lead room.",
        ],
        "follow_up": "What is the emotion of the shot: isolated, powerful, intimate?",
    },
    "camera_settings": {
        "title": "Camera Settings",
        "tips": [
            "Frame rate first: 24fps for cinematic look, 60fps+ for slow motion.",
            "Shutter speed about double your frame rate (24fps -> 1/48 or 1/50) for natural motion blur.",
            "Set aperture for depth of field, then use ISO and ND filters to expose correctly.",
            "Shoot Log/flat profiles for grading room, and set white balance manually.",
        ],
        "follow_up": "Which camera are you shooting on, and is it indoors or outdoors?",
    },
    "lighting": {
        "title": "Lighting",
        "tips": [
            "Basic setup: key light (main), fill (softens shadows), back/rim light (separates subject).",
            "Soft light flatters faces; hard light feels dramatic and gritty.",
            "Use practicals (lamps, neon, signs) as motivated light sources.",
            "Low-key = deep shadows and mood; high-key = bright and clean.",
        ],
        "follow_up": "What lights do you have and what mood do you want?",
    },
    "color_grading": {
        "title": "Color Grading",
        "tips": [
            "Correct first (exposure, white balance, contrast), then grade for style.",
            "Pick a palette: teal-orange for cinematic, desaturated for gritty, warm tones for nostalgia.",
            "Protect skin tones; check them on the vectorscope skin line.",
            "Add contrast with an S-curve and keep selective highlights for a punchy look.",
        ],
        "follow_up": "What look do you want: cinematic, nostalgic or gritty?",
    },
    "editing": {
        "title": "Editing",
        "tips": [
            "Build a rough cut first for story, then a fine cut for rhythm.",
            "Cut on action to hide cuts; use J and L cuts so audio leads or trails the picture.",
            "Match cuts and jump cuts add style; speed ramps add energy.",
            "Pacing follows emotion: fast cuts for tension, longer shots for reflection.",
        ],
        "follow_up": "What software are you editing in and what kind of scene is it?",
    },
    "sound_design": {
        "title": "Sound Design",
        "tips": [
            "Record clean dialogue first; always capture 30 seconds of room tone.",
            "Layer ambience, Foley and effects to make the world feel real.",
            "Music should support emotion, not fight dialogue. Duck it under speech.",
            "Silence is a tool: use it before an important moment for impact.",
        ],
        "follow_up": "Is this for dialogue, ambience, or a music-driven piece?",
    },
    "storyboarding_shotlist": {
        "title": "Storyboard and Shot List",
        "tips": [
            "Break each scene into shots: number, shot size, angle, movement, subject, notes.",
            "Stick figures are enough for a storyboard. Clarity beats beauty.",
            "Order the shot list by location and lighting setup, not by story order, to save time.",
            "Mark must-have shots versus nice-to-have shots.",
        ],
        "follow_up": "Tell me the scene and I can draft a shot list.",
    },
    "music_video_mode": {
        "title": "Music Video Mode",
        "tips": [
            "Plan performance coverage: wide, medium, close-up on the artist, and cutaway B-roll.",
            "Cut on the beat for energy; cut slightly off-beat for flow.",
            "Pick a visual motif matched to the genre (neon and cars for hip-hop, soft light for pop).",
            "Shoot multiple takes with lip-sync at the real song tempo.",
        ],
        "follow_up": "What is the genre and the location for your video?",
    },
    "troubleshooting": {
        "title": "Troubleshooting Visual Problems",
        "tips": [
            "Flat footage: you probably shot Log. Apply a LUT or add contrast and saturation.",
            "Noisy footage: lower ISO, add light, or use a denoiser in post.",
            "Shaky footage: use stabilization, a gimbal, or a tripod. Warp stabilizer helps in post.",
            "Blown highlights or muddy shadows: check exposure with zebras and the histogram next time.",
        ],
        "follow_up": "Can you describe exactly what looks wrong and what camera you used?",
    },
    "export_delivery": {
        "title": "Export and Delivery",
        "tips": [
            "YouTube: 16:9, H.264, high bitrate (e.g. 16-24 Mbps for 1080p).",
            "Reels/Shorts/TikTok: 9:16 at 1080x1920. Keep key content in the safe zone.",
            "Export a high-quality master first, then compress versions per platform.",
            "Check loudness (about -14 LUFS for most platforms) and file size limits.",
        ],
        "follow_up": "Which platform is the video going to?",
    },
    "equipment": {
        "title": "Equipment",
        "tips": [
            "Good audio and light usually matter more than a more expensive camera.",
            "Phones can shoot great video with a stabilizer, ND filter and manual app.",
            "Prime lenses (35mm, 50mm) are cheap, sharp and great in low light.",
            "Start with a tripod, one LED panel and a lav or shotgun mic.",
        ],
        "follow_up": "What is your budget and what are you shooting?",
    },
}

# Extra advice unlocked by detected context keywords.
CONTEXT_TIPS = {
    "night": "At night, use practical lights, neon or car headlights as sources and expose for highlights.",
    "music_video": "Plan performance takes and B-roll so you can cut on the beat in the edit.",
    "hip-hop": "Hip-hop visuals love low angles, strong rim light, and confident, slow tracking shots.",
    "documentary": "For documentary, capture B-roll and room tone, and keep the camera ready for unplanned moments.",
    "interview": "For interviews, use one soft key light at 45 degrees, a back light, and a lav mic.",
    "low budget": "On a low budget, limit locations and use natural light and practicals.",
    "car": "A car gives you reflections, headlight flares and interior shots. Use all three.",
    "reel": "For reels, hook in the first 2 seconds and shoot vertical 9:16.",
    "wedding": "For weddings, shoot the key moments with two angles and record clean audio of vows.",
    "dark": "For a dark look, underexpose slightly, crush shadows a little and keep selective highlights.",
    "isolated": "To show isolation, use wide frames, negative space and a small subject in the frame.",
}

INTENT_LABELS = {k: v["title"] for k, v in KNOWLEDGE.items()}

FILM_VOCAB = {
    "film", "movie", "video", "shot", "shoot", "shooting", "camera", "lens", "light", "lighting",
    "edit", "editing", "cut", "scene", "frame", "color", "colour", "grade", "grading", "sound",
    "audio", "music", "song", "story", "script", "storyboard", "footage", "export", "render",
    "reel", "vlog", "cinematic", "cinematography", "director", "directing", "actor", "mic",
    "tripod", "gimbal", "iso", "aperture", "shutter", "fps", "lut", "log", "documentary",
}
