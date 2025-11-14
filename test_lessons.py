"""
Test script for lesson loading system.
Run this to verify lessons are loading correctly.
"""

from models.lesson_loader import LessonLoader

def test_lesson_loading():
    """Test the lesson loading functionality."""

    print("=" * 70)
    print("LESSON LOADING TEST")
    print("=" * 70)

    # Create loader
    loader = LessonLoader()

    # Test 1: Discover lesson files
    print("\n1. Discovering lesson files...")
    available = loader.get_available_lesson_files()
    print(f"   Found {len(available)} lesson(s): {available}")

    if not available:
        print("   ⚠️  No lessons found in lessons/ directory")
        return

    # Test 2: Load a specific lesson
    print("\n2. Loading 'beginner_c_major' lesson...")
    lesson = loader.load_lesson("beginner_c_major")

    if lesson is None:
        print("   ❌ Failed to load lesson")
        return

    print(f"   ✓ Loaded: {lesson.name}")
    print(f"   ✓ Description: {lesson.description}")
    print(f"   ✓ Author: {lesson.author}")
    print(f"   ✓ Parts: {lesson.get_part_count()}")
    print(f"   ✓ Total duration: {lesson.get_total_duration_ms()}ms")

    # Test 3: Examine parts
    print("\n3. Examining parts...")
    for i, part in enumerate(lesson.parts):
        print(f"\n   Part {i+1}: {part.name}")
        print(f"      Notes to highlight: {len(part.notes_to_highlight)}")
        print(f"      Play sequence steps: {part.get_note_count()}")
        print(f"      Duration: {part.get_duration_ms()}ms")
        print(f"      Metadata: {part.metadata}")

    # Test 4: Load all lessons
    print("\n4. Loading all available lessons...")
    all_lessons = loader.load_all_lessons()
    print(f"   Successfully loaded {len(all_lessons)} lesson(s)")

    for lesson in all_lessons:
        print(f"   - {lesson.name} ({lesson.get_part_count()} parts)")

    # Test 5: Get lesson info
    print("\n5. Getting lesson info without full load...")
    for filename in available:
        info = loader.get_lesson_info(filename)
        if info:
            print(f"   {info['name']}:")
            print(f"      Filename: {info['filename']}")
            print(f"      Parts: {info['part_count']}")
            print(f"      Duration: {info['total_duration_ms']/1000:.1f}s")

    print("\n" + "=" * 70)
    print("✓ All tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    test_lesson_loading()
