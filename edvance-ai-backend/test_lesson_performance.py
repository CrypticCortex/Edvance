#!/usr/bin/env python3

import asyncio
import logging
import time
from datetime import datetime

from app.core.firebase import initialize_firebase
from app.agents.tools.lesson_tools import generate_lesson_content, generate_lesson_content_legacy, generate_lesson_content_optimized, generate_lesson_content_ultra_fast

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_lesson_generation_performance():
    """Test performance comparison between parallelized and legacy lesson generation."""
    try:
        # Initialize Firebase
        initialize_firebase()
        
        print("🚀 LESSON GENERATION PERFORMANCE TEST")
        print("=" * 60)
        
        test_params = {
            "learning_step_id": "test_step_fractions_perf",
            "student_id": "test_student_perf",
            "teacher_uid": "teacher_perf_test",
            "customizations": {
                "difficulty_adjustment": "normal",
                "learning_style": "visual",
                "include_interactive": True,
                "slide_count_preference": "medium"
            }
        }
        
        # Test ultra-fast version
        print("\n🚀 TESTING ULTRA-FAST VERSION")
        print("-" * 40)
        
        start_time = time.time()
        ultra_fast_result = await generate_lesson_content_ultra_fast(**test_params)
        ultra_fast_time = time.time() - start_time
        
        if ultra_fast_result.get("success"):
            metrics = ultra_fast_result.get("generation_metrics", {})
            print(f"✅ Ultra-Fast Generation: {ultra_fast_time:.2f}s")
            print(f"   📊 Slides Generated: {metrics.get('slides_generated', 0)}")
            print(f"   🔄 Data Gathering: {metrics.get('data_gathering_seconds', 0):.2f}s")
            print(f"   ⚡ AI Generation: {metrics.get('ai_generation_seconds', 0):.2f}s")
            print(f"   💾 Save Operations: {metrics.get('save_operations_seconds', 0):.2f}s")
            print(f"   🎯 Optimizations: {', '.join(metrics.get('speed_optimizations', []))}")
        else:
            print(f"❌ Ultra-Fast failed: {ultra_fast_result.get('error')}")
            ultra_fast_time = None
        
        # Test optimized version
        print("\n🚀 TESTING OPTIMIZED VERSION")
        print("-" * 40)
        
        start_time = time.time()
        optimized_result = await generate_lesson_content_optimized(**test_params)
        optimized_time = time.time() - start_time
        
        if optimized_result.get("success"):
            metrics = optimized_result.get("generation_metrics", {})
            print(f"✅ Optimized Generation: {optimized_time:.2f}s")
            print(f"   📊 Slides Generated: {metrics.get('slides_generated', 0)}")
            print(f"   🔄 Data Gathering: {metrics.get('data_gathering_seconds', 0):.2f}s")
            print(f"   🤖 AI Generation: {metrics.get('ai_generation_seconds', 0):.2f}s")
            print(f"   💾 Save Operations: {metrics.get('save_operations_seconds', 0):.2f}s")
            print(f"   🎯 API Calls Saved: {metrics.get('api_calls_saved', 0)}")
        else:
            print(f"❌ Optimized failed: {optimized_result.get('error')}")
            optimized_time = None
        
        # Test parallelized version
        print("\n⚡ TESTING PARALLELIZED VERSION")
        print("-" * 40)
        
        start_time = time.time()
        parallel_result = await generate_lesson_content(**test_params)
        parallel_time = time.time() - start_time
        
        if parallel_result.get("success"):
            metrics = parallel_result.get("generation_metrics", {})
            print(f"✅ Parallelized Generation: {parallel_time:.2f}s")
            print(f"   📊 Slides Generated: {metrics.get('slides_generated', 0)}")
            print(f"   🔄 Data Gathering: {metrics.get('data_gathering_seconds', 0):.2f}s")
            print(f"   🏗️  Structure Generation: {metrics.get('structure_generation_seconds', 0):.2f}s")
            print(f"   📝 Slide Generation: {metrics.get('slide_generation_seconds', 0):.2f}s")
            print(f"   💾 Save Operations: {metrics.get('save_operations_seconds', 0):.2f}s")
        else:
            print(f"❌ Parallelized failed: {parallel_result.get('error')}")
            return
        
        # Test legacy version for comparison (if available)
        print("\n🐌 TESTING LEGACY VERSION")
        print("-" * 40)
        
        try:
            start_time = time.time()
            legacy_result = await generate_lesson_content_legacy(**test_params)
            legacy_time = time.time() - start_time
            
            if legacy_result.get("success"):
                print(f"✅ Legacy Generation: {legacy_time:.2f}s")
                print(f"   📊 Slides Generated: {legacy_result.get('total_slides', 0)}")
            else:
                print(f"❌ Legacy failed: {legacy_result.get('error')}")
                legacy_time = None
        except Exception as e:
            print(f"❌ Legacy version not available: {str(e)}")
            legacy_time = None
        
        # Performance comparison
        print(f"\n📈 PERFORMANCE COMPARISON")
        print("=" * 60)
        
        times = []
        if ultra_fast_time:
            times.append(("Ultra-Fast", ultra_fast_time))
        if optimized_time:
            times.append(("Optimized", optimized_time))
        times.append(("Parallel", parallel_time))
        if legacy_time:
            times.append(("Legacy", legacy_time))
        
        # Sort by time (fastest first)
        times.sort(key=lambda x: x[1])
        
        print("🏆 RANKING (fastest to slowest):")
        for i, (name, time_val) in enumerate(times, 1):
            print(f"{i}. {name}: {time_val:.2f}s")
        
        if len(times) >= 2:
            fastest_time = times[0][1]
            slowest_time = times[-1][1]
            improvement = ((slowest_time - fastest_time) / slowest_time) * 100
            print(f"\n🚀 BEST IMPROVEMENT: {improvement:.1f}% faster ({times[0][0]} vs {times[-1][0]})")
        
        if optimized_time and legacy_time:
            opt_improvement = ((legacy_time - optimized_time) / legacy_time) * 100
            print(f"🎯 Optimized vs Legacy: {opt_improvement:.1f}% improvement")
        
        if optimized_time and parallel_time:
            par_comparison = ((parallel_time - optimized_time) / parallel_time) * 100
            print(f"⚡ Optimized vs Parallel: {par_comparison:.1f}% improvement")
        
        # Detailed breakdown for best performing version
        best_result = None
        best_time = float('inf')
        best_name = ""
        
        if ultra_fast_time and ultra_fast_time < best_time:
            best_result = ultra_fast_result
            best_time = ultra_fast_time
            best_name = "Ultra-Fast"
        
        if optimized_time and optimized_time < best_time:
            best_result = optimized_result
            best_time = optimized_time
            best_name = "Optimized"
        
        if parallel_time < best_time:
            best_result = parallel_result
            best_time = parallel_time
            best_name = "Parallel"
        
        if best_result.get("success"):
            metrics = best_result.get("generation_metrics", {})
            print(f"\n🔍 DETAILED TIMING BREAKDOWN ({best_name})")
            print("-" * 40)
            
            if best_name == "Ultra-Fast":
                print(f"Data Gathering:     {metrics.get('data_gathering_seconds', 0):.2f}s ({(metrics.get('data_gathering_seconds', 0)/best_time*100):.1f}%)")
                print(f"AI Generation:      {metrics.get('ai_generation_seconds', 0):.2f}s ({(metrics.get('ai_generation_seconds', 0)/best_time*100):.1f}%)")
                print(f"Save Operations:    {metrics.get('save_operations_seconds', 0):.2f}s ({(metrics.get('save_operations_seconds', 0)/best_time*100):.1f}%)")
            elif best_name == "Optimized":
                print(f"Data Gathering:     {metrics.get('data_gathering_seconds', 0):.2f}s ({(metrics.get('data_gathering_seconds', 0)/best_time*100):.1f}%)")
                print(f"AI Generation:      {metrics.get('ai_generation_seconds', 0):.2f}s ({(metrics.get('ai_generation_seconds', 0)/best_time*100):.1f}%)")
                print(f"Save Operations:    {metrics.get('save_operations_seconds', 0):.2f}s ({(metrics.get('save_operations_seconds', 0)/best_time*100):.1f}%)")
            else:
                print(f"Data Gathering:     {metrics.get('data_gathering_seconds', 0):.2f}s ({(metrics.get('data_gathering_seconds', 0)/best_time*100):.1f}%)")
                print(f"Structure Gen:      {metrics.get('structure_generation_seconds', 0):.2f}s ({(metrics.get('structure_generation_seconds', 0)/best_time*100):.1f}%)")
                print(f"Slide Generation:   {metrics.get('slide_generation_seconds', 0):.2f}s ({(metrics.get('slide_generation_seconds', 0)/best_time*100):.1f}%)")
                print(f"Save Operations:    {metrics.get('save_operations_seconds', 0):.2f}s ({(metrics.get('save_operations_seconds', 0)/best_time*100):.1f}%)")
            
            print(f"\n💡 OPTIMIZATION INSIGHTS")
            print("-" * 40)
            
            if best_name == "Optimized":
                slides_generated = metrics.get('slides_generated', 1)
                ai_time = metrics.get('ai_generation_seconds', 0)
                api_calls_saved = metrics.get('api_calls_saved', 0)
                print(f"Single AI call approach: {ai_time:.2f}s for {slides_generated} slides")
                print(f"API calls saved: {api_calls_saved}")
                print(f"Average time per slide: {(ai_time/slides_generated):.2f}s")
            else:
                slide_gen_time = metrics.get('slide_generation_seconds', 0)
                total_slides = metrics.get('slides_generated', 1)
                avg_slide_time = slide_gen_time / total_slides if total_slides > 0 else 0
                print(f"Parallel approach: {avg_slide_time:.2f}s per slide average")
                print(f"Parallelization efficiency: {metrics.get('parallel_optimization', False)}")
                
                if slide_gen_time > best_time * 0.6:
                    print("⚠️  Slide generation is the main bottleneck")
                    print("💡 Consider: Single AI call approach, prompt optimization")
        
        print(f"\n🎓 RECOMMENDATION")
        print("=" * 60)
        
        if best_time < 20:
            print("� EXCELLENT: Lesson generation under 20 seconds!")
            print("✅ Ready for production use")
        elif best_time < 40:
            print("✅ GOOD: Lesson generation under 40 seconds")
            print("🎯 Consider further optimizations for scale")
        elif best_time < 60:
            print("⚠️ ACCEPTABLE: Generation under 1 minute")
            print("💡 Room for improvement with caching or pre-generation")
        else:
            print("❌ NEEDS IMPROVEMENT: Generation over 1 minute")
            print("� Requires optimization before production")
        
        # Return comprehensive results
        return {
            "optimized_time": optimized_time,
            "parallel_time": parallel_time,
            "legacy_time": legacy_time,
            "best_approach": best_name,
            "best_time": best_time,
            "improvement_vs_legacy": ((legacy_time - best_time) / legacy_time * 100) if legacy_time else None,
            "metrics": best_result.get("generation_metrics", {})
        }
        
    except Exception as e:
        print(f"❌ Performance test failed: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(test_lesson_generation_performance())
