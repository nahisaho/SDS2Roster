"""
Performance benchmarking tests for SDS2Roster converter

These tests measure performance metrics for various dataset sizes.
Run with: pytest tests/benchmark/ -v
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pytest

from sds2roster.converter import SDSToOneRosterConverter
from sds2roster.models.sds import (
    SDSSchool,
    SDSSection,
    SDSStudent,
    SDSEnrollment,
    SDSTeacher,
    SDSDataModel,
)


def generate_test_data(num_students: int = 1000, num_courses: int = 100) -> Dict[str, List]:
    """Generate test SDS data of specified size."""
    print(f"\nGenerating test data: {num_students} students, {num_courses} courses...")

    # Generate schools
    schools = [
        SDSSchool(
            sis_id=f"SCHOOL{i}",
            name=f"Test School {i}",
            school_number=f"SCH{i:04d}",
        )
        for i in range(max(1, num_students // 100))
    ]

    # Generate students
    students = [
        SDSStudent(
            sis_id=f"STU{i:06d}",
            school_sis_id=schools[i % len(schools)].sis_id,
            username=f"student{i}",
            first_name=f"First{i}",
            last_name=f"Last{i}",
            email=f"student{i}@test.com",
            grade="10",
        )
        for i in range(num_students)
    ]

    # Generate teachers
    num_teachers = max(10, num_courses // 5)
    teachers = [
        SDSTeacher(
            sis_id=f"TCH{i:04d}",
            school_sis_id=schools[i % len(schools)].sis_id,
            username=f"teacher{i}",
            first_name=f"Teacher{i}",
            last_name=f"Last{i}",
            email=f"teacher{i}@test.com",
        )
        for i in range(num_teachers)
    ]

    # Generate sections (courses)
    sections = [
        SDSSection(
            sis_id=f"SEC{i:06d}",
            school_sis_id=schools[i % len(schools)].sis_id,
            section_name=f"Course {i}",
            section_number=f"COURSE{i:04d}",
            term_sis_id="TERM2024",
            term_name="2024 Fall",
            term_start_date=datetime(2024, 9, 1),
            term_end_date=datetime(2024, 12, 20),
            course_subject="Mathematics",
        )
        for i in range(num_courses)
    ]

    # Generate enrollments (students in courses)
    enrollments = []
    students_per_course = max(5, num_students // num_courses)
    for section in sections:
        # Assign random students to each section
        section_students = students[: min(students_per_course, len(students))]
        for student in section_students:
            enrollments.append(
                SDSEnrollment(
                    section_sis_id=section.sis_id,
                    sis_id=student.sis_id,
                    role="student",
                )
            )

    return {
        "schools": schools,
        "students": students,
        "teachers": teachers,
        "sections": sections,
        "enrollments": enrollments,
    }


class TestPerformance:
    """Performance benchmarking tests."""

    @pytest.mark.benchmark
    def test_small_dataset_1k(self, tmp_path):
        """Benchmark: 1,000 students, 100 courses"""
        self._run_benchmark(tmp_path, num_students=1_000, num_courses=100, name="1K")

    @pytest.mark.benchmark
    def test_medium_dataset_10k(self, tmp_path):
        """Benchmark: 10,000 students, 500 courses"""
        self._run_benchmark(tmp_path, num_students=10_000, num_courses=500, name="10K")

    @pytest.mark.benchmark
    @pytest.mark.slow
    def test_large_dataset_100k(self, tmp_path):
        """Benchmark: 100,000 students, 2,000 courses"""
        self._run_benchmark(tmp_path, num_students=100_000, num_courses=2_000, name="100K")

    def _run_benchmark(self, tmp_path: Path, num_students: int, num_courses: int, name: str):
        """Run benchmark test for specific dataset size."""
        print(f"\n{'='*60}")
        print(f"Benchmark: {name} Dataset")
        print(f"Students: {num_students:,}, Courses: {num_courses:,}")
        print(f"{'='*60}")

        # Generate test data
        start_gen = time.time()
        test_data = generate_test_data(num_students, num_courses)
        gen_time = time.time() - start_gen
        print(f"Test data generated in {gen_time:.2f}s")

        # Create temporary SDS directory
        sds_dir = tmp_path / "sds"
        sds_dir.mkdir()

        # Write SDS CSV files
        start_write = time.time()
        self._write_csv(sds_dir / "School.csv", test_data["schools"])
        self._write_csv(sds_dir / "Student.csv", test_data["students"])
        self._write_csv(sds_dir / "Teacher.csv", test_data["teachers"])
        self._write_csv(sds_dir / "Section.csv", test_data["sections"])
        self._write_csv(sds_dir / "StudentEnrollment.csv", test_data["enrollments"])
        write_time = time.time() - start_write
        print(f"CSV files written in {write_time:.2f}s")

        # Run conversion
        converter = SDSToOneRosterConverter()
        sds_data_model = SDSDataModel(
            schools=test_data["schools"],
            students=test_data["students"],
            teachers=test_data["teachers"],
            sections=test_data["sections"],
            enrollments=test_data["enrollments"],
        )

        start_convert = time.time()
        result = converter.convert(sds_data_model)
        convert_time = time.time() - start_convert

        # Calculate stats
        total_records = sum(len(v) for v in test_data.values())
        records_per_sec = total_records / convert_time if convert_time > 0 else 0

        # Print results
        print(f"\nConversion Results:")
        print(f"  • Total time: {convert_time:.2f}s")
        print(f"  • Records/second: {records_per_sec:,.0f}")
        print(f"  • Organizations: {len(result.orgs)}")
        print(f"  • Users: {len(result.users)}")
        print(f"  • Courses: {len(result.courses)}")
        print(f"  • Classes: {len(result.classes)}")
        print(f"  • Enrollments: {len(result.enrollments)}")
        print(f"  • Academic Sessions: {len(result.academic_sessions)}")

        # Performance assertions
        assert convert_time < 60, f"Conversion took too long: {convert_time:.2f}s"
        assert records_per_sec > 100, f"Too slow: {records_per_sec:.0f} records/sec"

        # Verify results
        assert len(result.orgs) > 0
        assert len(result.users) > 0
        assert len(result.courses) > 0
        assert len(result.classes) > 0
        assert len(result.enrollments) > 0

        print(f"{'='*60}\n")

    def _write_csv(self, path: Path, data: List):
        """Write data to CSV file."""
        if not data:
            return

        import csv

        with open(path, "w", newline="", encoding="utf-8") as f:
            if hasattr(data[0], "model_dump"):
                # Pydantic model
                writer = csv.DictWriter(f, fieldnames=data[0].model_dump().keys())
                writer.writeheader()
                for item in data:
                    writer.writerow(item.model_dump())
            else:
                # Dict
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)


class TestMemoryUsage:
    """Memory usage tests."""

    @pytest.mark.benchmark
    def test_memory_efficiency(self, tmp_path):
        """Test memory usage during conversion."""
        import tracemalloc

        # Generate test data
        test_data = generate_test_data(num_students=10_000, num_courses=500)

        # Start memory tracking
        tracemalloc.start()

        # Run conversion
        converter = SDSToOneRosterConverter()
        sds_data_model = SDSDataModel(
            schools=test_data["schools"],
            students=test_data["students"],
            teachers=test_data["teachers"],
            sections=test_data["sections"],
            enrollments=test_data["enrollments"],
        )
        converter.convert(sds_data_model)

        # Get memory stats
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Print results
        print(f"\nMemory Usage:")
        print(f"  • Current: {current / 1024 / 1024:.2f} MB")
        print(f"  • Peak: {peak / 1024 / 1024:.2f} MB")

        # Memory should be reasonable (< 500MB for 10K students)
        assert peak < 500 * 1024 * 1024, f"Peak memory too high: {peak / 1024 / 1024:.2f}MB"
