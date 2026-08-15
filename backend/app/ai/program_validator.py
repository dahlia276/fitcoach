from app.models.training_profile import TrainingProfile
from app.models.workout_program import WorkoutProgram


class ProgramValidator:
    """
    Applies deterministic quality checks to generated workout programs.
    """

    def validate(
        self,
        program: WorkoutProgram,
        profile: TrainingProfile,
        valid_exercise_ids: set[str] | None = None,
    ) -> WorkoutProgram:
        self._remove_duplicate_exercises(program)
        self._validate_session_duration(program, profile)

        if valid_exercise_ids is not None:
            self._enforce_experience_level(program, valid_exercise_ids)

        return program

    def _remove_duplicate_exercises(
        self,
        program: WorkoutProgram,
    ) -> None:
        """
        Removes duplicate exercises within each workout while preserving order.
        """

        for day in program.days:
            seen = set()
            unique_exercises = []

            for exercise in day.exercises:
                if exercise.exercise_id in seen:
                    continue

                seen.add(exercise.exercise_id)
                unique_exercises.append(exercise)

            day.exercises = unique_exercises

    def _validate_session_duration(
        self,
        program: WorkoutProgram,
        profile: TrainingProfile,
    ) -> None:
        """
        Warn if the generated duration exceeds the user's requested duration.
        """

        requested = profile.session_minutes

        for day in program.days:
            estimated = day.estimated_duration_minutes

            if estimated > requested:
                print(
                    f"[ProgramValidator] "
                    f"{day.name} exceeds requested duration "
                    f"({estimated} > {requested} min)"
                )

    def _enforce_experience_level(
        self,
        program: WorkoutProgram,
        valid_exercise_ids: set[str],
    ) -> None:
        """
        Drops any exercise the model picked outside the experience-level-
        filtered retrieval set, guaranteeing the program only contains
        exercises that match the user's chosen experience level.
        """

        for day in program.days:
            kept = [
                exercise
                for exercise in day.exercises
                if exercise.exercise_id in valid_exercise_ids
            ]

            dropped = len(day.exercises) - len(kept)

            if dropped:
                print(
                    f"[ProgramValidator] Dropped {dropped} exercise(s) from "
                    f"{day.name} that didn't match the requested experience level."
                )

            day.exercises = kept