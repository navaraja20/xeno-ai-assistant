"""
Performance Profiling Script for XENO AI Assistant
Profiles critical operations to identify bottlenecks
"""

import cProfile
import pstats
import io
import time
from pathlib import Path
from memory_profiler import profile as memory_profile
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))


class PerformanceProfiler:
    """Profile performance of XENO components"""
    
    def __init__(self):
        self.results = {}
        
    def profile_encryption(self):
        """Profile encryption/decryption operations"""
        print("\n=== Profiling Encryption Operations ===")
        from src.security.enterprise_security import EncryptionManager
        
        profiler = cProfile.Profile()
        enc_manager = EncryptionManager()
        
        # Profile encryption
        test_data = "This is test data " * 100  # 1.9KB
        profiler.enable()
        
        start = time.perf_counter()
        for _ in range(100):
            encrypted = enc_manager.encrypt_data(test_data)
            decrypted = enc_manager.decrypt_data(encrypted)
        elapsed = time.perf_counter() - start
        
        profiler.disable()
        
        # Print stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        
        self.results['encryption'] = {
            'operations': 200,  # 100 encrypt + 100 decrypt
            'total_time': elapsed,
            'avg_time_ms': (elapsed / 200) * 1000,
            'ops_per_sec': 200 / elapsed
        }
        
        print(f"Total time: {elapsed:.3f}s")
        print(f"Average per operation: {(elapsed/200)*1000:.2f}ms")
        print(f"Operations/sec: {200/elapsed:.1f}")
        print("\nTop 10 functions:")
        print(s.getvalue()[:1000])
        
    def profile_password_hashing(self):
        """Profile password hashing operations"""
        print("\n=== Profiling Password Hashing ===")
        from src.security.enterprise_security import EncryptionManager
        
        profiler = cProfile.Profile()
        enc_manager = EncryptionManager()
        
        profiler.enable()
        start = time.perf_counter()
        
        for i in range(10):
            password = f"TestPassword{i}!@#"
            hashed, salt = enc_manager.hash_password(password)
            verified = enc_manager.verify_password(password, hashed, salt)
        
        elapsed = time.perf_counter() - start
        profiler.disable()
        
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        
        self.results['password_hashing'] = {
            'operations': 20,  # 10 hash + 10 verify
            'total_time': elapsed,
            'avg_time_ms': (elapsed / 20) * 1000,
            'ops_per_sec': 20 / elapsed
        }
        
        print(f"Total time: {elapsed:.3f}s")
        print(f"Average per operation: {(elapsed/20)*1000:.2f}ms")
        print(f"Operations/sec: {20/elapsed:.1f}")
        print("\nTop 10 functions:")
        print(s.getvalue()[:1000])
        
    def profile_ai_personalization(self):
        """Profile AI personalization operations"""
        print("\n=== Profiling AI Personalization ===")
        from src.ai.model_finetuning import PersonalizationEngine
        
        profiler = cProfile.Profile()
        engine = PersonalizationEngine("test_user")
        
        profiler.enable()
        start = time.perf_counter()
        
        # Simulate user interactions
        for i in range(50):
            engine.update_preference(f"feature_{i%10}", f"value_{i}")
            engine.record_interaction(
                query=f"command_{i%5}",
                response=f"response_{i}",
                context={"test": f"context_{i}"}
            )
            
        # Generate personalized prompts
        for i in range(20):
            engine.generate_training_examples(f"Base prompt {i}", f"response {i}")
        
        elapsed = time.perf_counter() - start
        profiler.disable()
        
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        
        self.results['ai_personalization'] = {
            'operations': 120,  # 50 prefs + 50 interactions + 20 prompts
            'total_time': elapsed,
            'avg_time_ms': (elapsed / 120) * 1000,
            'ops_per_sec': 120 / elapsed
        }
        
        print(f"Total time: {elapsed:.3f}s")
        print(f"Average per operation: {(elapsed/120)*1000:.2f}ms")
        print(f"Operations/sec: {120/elapsed:.1f}")
        print("\nTop 10 functions:")
        print(s.getvalue()[:1000])
        
    def profile_team_collaboration(self):
        """Profile team collaboration operations"""
        print("\n=== Profiling Team Collaboration ===")
        from src.collaboration.team_features import TeamManager, TaskDelegationManager
        
        profiler = cProfile.Profile()
        team_mgr = TeamManager()
        task_mgr = TaskDelegationManager()
        
        profiler.enable()
        start = time.perf_counter()
        
        # Create teams
        for i in range(10):
            team_id = f"team_{i}"
            team_mgr.create_team(
                team_id=team_id,
                name=f"Team {i}",
                description=f"Test team {i}",
                owner=f"owner_{i}"
            )
            # Add members
            for j in range(5):
                team_mgr.add_member(team_id, f"member_{i}_{j}", "member")
            
            # Assign tasks
            for j in range(10):
                task_mgr.assign_task(
                    task_id=f"task_{i}_{j}",
                    title=f"Task {j}",
                    description=f"Description {j}",
                    assigned_to=f"member_{i}_{j%5}",
                    assigned_by=f"owner_{i}",
                    team_id=team_id
                )
        
        elapsed = time.perf_counter() - start
        profiler.disable()
        
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        
        self.results['collaboration'] = {
            'operations': 160,  # 10 teams + 50 members + 100 tasks
            'total_time': elapsed,
            'avg_time_ms': (elapsed / 160) * 1000,
            'ops_per_sec': 160 / elapsed
        }
        
        print(f"Total time: {elapsed:.3f}s")
        print(f"Average per operation: {(elapsed/160)*1000:.2f}ms")
        print(f"Operations/sec: {160/elapsed:.1f}")
        print("\nTop 10 functions:")
        print(s.getvalue()[:1000])
        
    def profile_iot_operations(self):
        """Profile IoT device operations"""
        print("\n=== Profiling IoT Operations ===")
        from src.iot.smart_home_integration import SmartHomeHub, SmartLight, SmartThermostat
        
        profiler = cProfile.Profile()
        hub = SmartHomeHub(api_endpoint="http://test.local", api_key="test_key")
        
        profiler.enable()
        start = time.perf_counter()
        
        # Add devices
        for i in range(20):
            light = SmartLight(f'light_{i}', f'Living Room Light {i}')
            hub.register_device(light)
            
            thermo = SmartThermostat(f'thermo_{i}', f'Thermostat {i}')
            hub.register_device(thermo)
        
        # Get devices
        for i in range(100):
            hub.get_device(f'light_{i%20}')
            devices = hub.get_devices_by_type('light')
        
        elapsed = time.perf_counter() - start
        profiler.disable()
        
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        
        self.results['iot_operations'] = {
            'operations': 240,  # 40 adds + 200 gets
            'total_time': elapsed,
            'avg_time_ms': (elapsed / 240) * 1000,
            'ops_per_sec': 240 / elapsed
        }
        
        print(f"Total time: {elapsed:.3f}s")
        print(f"Average per operation: {(elapsed/240)*1000:.2f}ms")
        print(f"Operations/sec: {240/elapsed:.1f}")
        print("\nTop 10 functions:")
        print(s.getvalue()[:1000])
        
    def profile_security_config(self):
        """Profile security configuration helpers"""
        print("\n=== Profiling Security Config ===")
        from src.security.security_config import (
            PasswordValidator, InputSanitizer, RateLimiter
        )
        
        profiler = cProfile.Profile()
        
        profiler.enable()
        start = time.perf_counter()
        
        # Password validation
        for i in range(100):
            password = f"TestPass{i}!@#XYZ"
            PasswordValidator.validate(password)
        
        # Input sanitization
        for i in range(100):
            InputSanitizer.sanitize_email(f"test{i}@example.com")
            InputSanitizer.sanitize_username(f"user_{i}")
            InputSanitizer.sanitize_filename(f"file_{i}.txt")
        
        # Rate limiting
        limiter = RateLimiter()
        for i in range(100):
            limiter.is_allowed(f"user_{i%10}", max_requests=5, window_seconds=60)
        
        elapsed = time.perf_counter() - start
        profiler.disable()
        
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        
        self.results['security_config'] = {
            'operations': 500,  # 100 validate + 300 sanitize + 100 rate limit
            'total_time': elapsed,
            'avg_time_ms': (elapsed / 500) * 1000,
            'ops_per_sec': 500 / elapsed
        }
        
        print(f"Total time: {elapsed:.3f}s")
        print(f"Average per operation: {(elapsed/500)*1000:.2f}ms")
        print(f"Operations/sec: {500/elapsed:.1f}")
        print("\nTop 10 functions:")
        print(s.getvalue()[:1000])
        
    def generate_report(self):
        """Generate performance report"""
        print("\n" + "="*70)
        print("PERFORMANCE PROFILING REPORT")
        print("="*70)
        
        for name, metrics in self.results.items():
            print(f"\n{name.upper().replace('_', ' ')}:")
            print(f"  Total Operations: {metrics['operations']}")
            print(f"  Total Time: {metrics['total_time']:.3f}s")
            print(f"  Average Time: {metrics['avg_time_ms']:.2f}ms")
            print(f"  Throughput: {metrics['ops_per_sec']:.1f} ops/sec")
            
            # Performance rating
            avg_ms = metrics['avg_time_ms']
            if avg_ms < 10:
                rating = "EXCELLENT (5/5)"
            elif avg_ms < 50:
                rating = "GOOD (4/5)"
            elif avg_ms < 100:
                rating = "ACCEPTABLE (3/5)"
            elif avg_ms < 500:
                rating = "NEEDS OPTIMIZATION (2/5)"
            else:
                rating = "CRITICAL - SLOW (1/5)"
            
            print(f"  Rating: {rating}")
        
        # Overall summary
        total_ops = sum(m['operations'] for m in self.results.values())
        total_time = sum(m['total_time'] for m in self.results.values())
        avg_overall = (total_time / total_ops) * 1000
        
        print("\n" + "="*70)
        print("OVERALL SUMMARY:")
        print(f"  Total Operations Profiled: {total_ops}")
        print(f"  Total Time: {total_time:.3f}s")
        print(f"  Overall Average: {avg_overall:.2f}ms per operation")
        print("="*70)
        
        # Identify bottlenecks
        print("\nBOTTLENECKS (slowest operations):")
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]['avg_time_ms'],
            reverse=True
        )
        
        for i, (name, metrics) in enumerate(sorted_results[:3], 1):
            print(f"  {i}. {name}: {metrics['avg_time_ms']:.2f}ms")
        
        print("\n")


def main():
    """Run all performance profiles"""
    profiler = PerformanceProfiler()
    
    print("Starting Performance Profiling...")
    print("This will take a few minutes...\n")
    
    try:
        profiler.profile_encryption()
    except Exception as e:
        print(f"Error profiling encryption: {e}")
    
    try:
        profiler.profile_password_hashing()
    except Exception as e:
        print(f"Error profiling password hashing: {e}")
    
    try:
        profiler.profile_ai_personalization()
    except Exception as e:
        print(f"Error profiling AI personalization: {e}")
    
    try:
        profiler.profile_team_collaboration()
    except Exception as e:
        print(f"Error profiling team collaboration: {e}")
    
    try:
        profiler.profile_iot_operations()
    except Exception as e:
        print(f"Error profiling IoT operations: {e}")
    
    try:
        profiler.profile_security_config()
    except Exception as e:
        print(f"Error profiling security config: {e}")
    
    # Generate final report
    profiler.generate_report()


if __name__ == "__main__":
    main()
