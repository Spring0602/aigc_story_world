from schemas import ImagePrompt, SceneCard


class ImagePromptGenerator:
    def generate(self, scene: SceneCard) -> ImagePrompt:
        return ImagePrompt(
            prompt_cn=(
                f"{scene.visual_style}，{scene.time}，{scene.location}，"
                f"{scene.main_action}，{scene.lighting}，气氛{scene.atmosphere}，"
                "第三人称限知视角，电影感光影。"
            ),
            prompt_en=(
                f"{scene.visual_style}, {scene.time}, {scene.location}, "
                f"{scene.main_action}, {scene.lighting}, {scene.atmosphere}, "
                "third-person limited perspective, cinematic lighting"
            ),
            negative_prompt_cn="多人主角，白天，夸张科幻机器，低质量，模糊",
            negative_prompt_en="multiple protagonists, daylight, exaggerated sci-fi machinery, low quality, blurry",
        )
