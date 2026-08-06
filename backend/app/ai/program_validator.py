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
    ) -> WorkoutProgram:
        self._remove_duplicate_exercises(program)
        self._validate_session_duration(program, profile)

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