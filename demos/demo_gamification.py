"""
Demo: Gamification System
Demonstrates XP, achievements, streaks, and leaderboards
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict

from src.core.logger import setup_logger
from src.gamification import (
    get_xp_system,
    get_achievement_system,
    get_streak_system,
    get_leaderboard_system,
)


logger = setup_logger("demo.gamification")


def demo_xp_system():
    """Demonstrate XP system"""
    print("\n" + "=" * 70)
    print("DEMO: XP System")
    print("=" * 70)

    xp_system = get_xp_system()

    # Award XP for various activities
    print("\n⭐ Earning XP:")

    activities = [
        ("task_complete", 1.0, "Completed first task"),
        ("task_complete_early", 1.0, "Finished task ahead of schedule"),
        ("email_sent", 1.0, "Sent important email"),
        ("focus_session", 1.0, "Completed 1-hour focus session"),
        ("task_complete", 2.0, "Completed urgent task (2x multiplier)"),
    ]

    for event_type, multiplier, description in activities:
        result = xp_system.award_xp(event_type, multiplier, description)
        
        print(f"\n   {description}")
        print(f"   + {result['xp_awarded']} XP (Total: {result['total_xp']})")
        
        if result['level_up']:
            print(f"   🎉 LEVEL UP! Now level {result['new_level']}")
        else:
            print(f"   Progress: {xp_system.get_progress_to_next_level():.1f}% to level {result['new_level'] + 1}")

    # Show stats
    print("\n📊 XP Statistics:")
    stats = xp_system.get_stats()
    print(f"   Level: {stats['current_level']}")
    print(f"   Total XP: {stats['total_xp']}")
    print(f"   XP to next level: {stats['xp_to_next_level']}")
    print(f"   Progress: {stats['progress_percent']:.1f}%")
    print(f"   Total events: {stats['total_events']}")

    print(f"\n   XP by activity type:")
    for event_type, xp in stats['xp_by_type'].items():
        print(f"   - {event_type}: {xp} XP")


def demo_achievements():
    """Demonstrate achievement system"""
    print("\n" + "=" * 70)
    print("DEMO: Achievement System")
    print("=" * 70)

    achievement_system = get_achievement_system()

    # Track events
    print("\n🏆 Tracking achievements:")

    events = [
        ("task_complete", 1, "First task"),
        ("task_complete", 4, "More tasks"),
        ("focus_session", 1, "Focus session"),
        ("consecutive_days", 1, "Daily login"),
    ]

    for event_type, count, description in events:
        print(f"\n   {description} ({event_type} +{count})")
        unlocked = achievement_system.track_event(event_type, count)
        
        if unlocked:
            for achievement in unlocked:
                print(f"   🎉 ACHIEVEMENT UNLOCKED: {achievement.icon} {achievement.name}")
                print(f"      {achievement.description}")
                print(f"      +{achievement.xp_reward} XP")
        else:
            print(f"      No achievements unlocked")

    # Show progress
    print("\n📊 Achievement Progress:")
    stats = achievement_system.get_progress_stats()
    print(f"   Total: {stats['total_achievements']}")
    print(f"   Unlocked: {stats['unlocked']}")
    print(f"   Locked: {stats['locked']}")
    print(f"   Completion: {stats['completion_percent']:.1f}%")
    print(f"   XP Earned: {stats['total_xp_earned']}")

    # Show categories
    print(f"\n   By Category:")
    for category, cat_stats in stats['categories'].items():
        print(f"   - {category}: {cat_stats['unlocked']}/{cat_stats['total']}")

    # Show unlocked achievements
    print(f"\n🏅 Unlocked Achievements:")
    for achievement in achievement_system.get_unlocked_achievements():
        print(f"   {achievement.icon} {achievement.name} - {achievement.description}")

    # Show locked achievements (non-secret)
    print(f"\n🔒 Locked Achievements (Next to unlock):")
    for achievement in achievement_system.get_locked_achievements()[:5]:
        progress_pct = (achievement.progress / achievement.max_progress * 100) if achievement.max_progress > 0 else 0
        print(f"   {achievement.icon} {achievement.name}")
        print(f"      Progress: {achievement.progress}/{achievement.max_progress} ({progress_pct:.0f}%)")


def demo_streaks():
    """Demonstrate streak system"""
    print("\n" + "=" * 70)
    print("DEMO: Streak System")
    print("=" * 70)

    streak_system = get_streak_system()

    # Record daily activities
    print("\n🔥 Recording daily activities:")

    activities = [
        ("daily_login", "Logged in today"),
        ("task_completion", "Completed tasks today"),
        ("focus_session", "Completed focus session"),
    ]

    for streak_type, description in activities:
        result = streak_system.record_activity(streak_type)
        
        print(f"\n   {description}")
        
        if result['already_recorded']:
            print(f"   ℹ️  Already recorded today")
        else:
            print(f"   ✓ Recorded!")
            print(f"   🔥 Current streak: {result['current_streak']} days")
            print(f"   🏆 Longest streak: {result['longest_streak']} days")
            
            if result['milestone_reached']:
                print(f"   🎉 MILESTONE: {result['milestone_reached']} days!")

    # Show all streaks
    print("\n📊 All Streaks:")
    for streak in streak_system.get_all_streaks():
        status = "🔥" if streak.current_streak > 0 else "💤"
        print(f"\n   {status} {streak.icon} {streak.name}")
        print(f"      Current: {streak.current_streak} days")
        print(f"      Longest: {streak.longest_streak} days")
        print(f"      Total days: {streak.total_days}")

    # Show stats
    print("\n📈 Streak Statistics:")
    stats = streak_system.get_stats()
    print(f"   Total streaks tracked: {stats['total_streaks']}")
    print(f"   Active streaks: {stats['active_streaks']}")
    print(f"   Longest current: {stats['longest_current']} days")
    print(f"   Longest ever: {stats['longest_ever']} days")
    print(f"   Total activity days: {stats['total_days']}")


def demo_leaderboards():
    """Demonstrate leaderboard system"""
    print("\n" + "=" * 70)
    print("DEMO: Leaderboard System")
    print("=" * 70)

    leaderboard_system = get_leaderboard_system()

    # Simulate multiple users
    print("\n👥 Simulating leaderboard with multiple users:")

    users = [
        ("user_1", "Alice", 2500),
        ("user_2", "Bob", 1800),
        ("user_3", "Charlie", 3200),
        ("user_4", "Diana", 2100),
        ("user_5", "Eve", 2900),
        ("current_user", "You", 2400),
    ]

    for user_id, username, xp in users:
        leaderboard_system.update_score("xp_all_time", user_id, username, xp)
        print(f"   Added {username}: {xp} XP")

    # Show top 10
    print("\n🏆 XP Leaderboard (Top 10):")
    top_entries = leaderboard_system.get_top("xp_all_time", limit=10)
    
    for entry in top_entries:
        rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(entry.rank, f"#{entry.rank}")
        highlight = " ← YOU" if entry.user_id == "current_user" else ""
        print(f"   {rank_emoji} {entry.username}: {entry.score} XP{highlight}")

    # Show user stats
    print("\n📊 Your Stats Across Leaderboards:")
    user_stats = leaderboard_system.get_user_stats("current_user")
    
    for lb_id, stats in user_stats.items():
        leaderboard = leaderboard_system.get_leaderboard(lb_id)
        print(f"\n   {leaderboard.name}:")
        print(f"   Rank: #{stats['rank']} of {stats['total_entries']}")
        print(f"   Score: {stats['score']}")


def demo_integration():
    """Demonstrate integrated gamification"""
    print("\n" + "=" * 70)
    print("DEMO: Integrated Gamification Flow")
    print("=" * 70)

    xp_system = get_xp_system()
    achievement_system = get_achievement_system()
    streak_system = get_streak_system()
    leaderboard_system = get_leaderboard_system()

    print("\n🎮 Simulating daily workflow:")

    # 1. Daily login
    print("\n1️⃣ Daily Login")
    streak_result = streak_system.record_activity("daily_login")
    xp_result = xp_system.award_xp("first_login_day")
    achievements = achievement_system.track_event("first_login", 1)
    
    print(f"   ✓ Logged in")
    print(f"   🔥 {streak_result['current_streak']} day streak")
    print(f"   ⭐ +{xp_result['xp_awarded']} XP")
    
    if achievements:
        print(f"   🏆 Unlocked: {achievements[0].name}")

    # 2. Complete tasks
    print("\n2️⃣ Complete Tasks")
    for i in range(3):
        xp_result = xp_system.award_xp("task_complete")
        achievements = achievement_system.track_event("task_complete", 1)
        
        print(f"   ✓ Task {i+1} completed (+{xp_result['xp_awarded']} XP)")
        
        if xp_result['level_up']:
            print(f"      🎉 Level up to {xp_result['new_level']}!")

    streak_system.record_activity("task_completion")

    # 3. Focus session
    print("\n3️⃣ Focus Session")
    xp_result = xp_system.award_xp("focus_session")
    streak_system.record_activity("focus_session")
    achievements = achievement_system.track_event("focus_session", 1)
    
    print(f"   ✓ Completed focus session")
    print(f"   ⭐ +{xp_result['xp_awarded']} XP")

    # 4. Update leaderboard
    print("\n4️⃣ Update Leaderboard")
    leaderboard_system.update_score(
        "xp_all_time",
        "current_user",
        "You",
        xp_result['total_xp']
    )
    
    rank = leaderboard_system.get_user_rank("xp_all_time", "current_user")
    print(f"   📊 Your rank: #{rank}")

    # Show summary
    print("\n📈 Daily Summary:")
    xp_stats = xp_system.get_stats()
    achievement_stats = achievement_system.get_progress_stats()
    streak_stats = streak_system.get_stats()
    
    print(f"   Level: {xp_stats['current_level']}")
    print(f"   Total XP: {xp_stats['total_xp']}")
    print(f"   Achievements: {achievement_stats['unlocked']}/{achievement_stats['total_achievements']}")
    print(f"   Active streaks: {streak_stats['active_streaks']}")
    print(f"   Longest streak: {streak_stats['longest_current']} days")


def demo_performance():
    """Demonstrate performance metrics"""
    print("\n" + "=" * 70)
    print("DEMO: Performance Metrics")
    print("=" * 70)

    xp_system = get_xp_system()
    achievement_system = get_achievement_system()

    # XP system performance
    print("\n⏱️  XP System Performance:")
    start = time.time()
    for _ in range(100):
        xp_system.award_xp("task_complete")
    elapsed = (time.time() - start) * 1000
    print(f"   100 XP awards: {elapsed:.2f}ms ({elapsed/100:.3f}ms each)")

    # Achievement tracking performance
    print("\n⏱️  Achievement Tracking Performance:")
    start = time.time()
    for _ in range(100):
        achievement_system.track_event("task_complete", 1)
    elapsed = (time.time() - start) * 1000
    print(f"   100 event tracks: {elapsed:.2f}ms ({elapsed/100:.3f}ms each)")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("XENO GAMIFICATION SYSTEM - COMPREHENSIVE DEMO")
    print("=" * 70)

    try:
        # XP system
        demo_xp_system()

        # Achievements
        demo_achievements()

        # Streaks
        demo_streaks()

        # Leaderboards
        demo_leaderboards()

        # Integration
        demo_integration()

        # Performance
        demo_performance()

        print("\n" + "=" * 70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()
