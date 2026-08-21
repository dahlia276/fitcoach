from app.models.training_profile import TrainingProfile


def build_training_profile(user: dict) -> TrainingProfile:
    """
    Business rules for creating a training profile.

    These rules are deterministic and do not require an LLM.
    """

    experience = user["experience"].strip().lower()

    if experience == "beginner":
        return TrainingProfile(
            goal=user["goal"],
            experience=user["experience"],
            equipment=user["equipment"],
            injuries=user["injuries"],
            training_days=user.get("training_days") or 3,
            session_minutes=user.get("session_minutes") or 60,
            recommended_split="Full Body",
            reasoning=(
                "A full body split maximizes practice of compound lifts "
                "while allowing sufficient recovery."
            ),
        )

    if experience == "intermediate":
        return TrainingProfile(
            goal=user["goal"],
            experience=user["experience"],
            equipment=user["equipment"],
            injuries=user["injuries"],
            training_days=user.get("training_days") or 4,
            session_minutes=user.get("session_minutes") or 60,
            recommended_split="Upper / Lower",
            reasoning=(
                "A 4-day upper/lower split provides increased training volume "
                "and recovery between muscle groups."
            ),
        )

    return TrainingProfile(
        goal=user["goal"],
        experience=user["experience"],
        equipment=user["equipment"],
        injuries=user["injuries"],
        training_days=user.get("training_days") or 5,
        session_minutes=user.get("session_minutes") or 75,
        recommended_split="Push / Pull / Legs",
        reasoning=(
            "An experienced lifter can recover from higher training frequency "
            "and volume."
        ),
    )
