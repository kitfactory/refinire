#!/usr/bin/env python3
"""
Investigate ModelSettings Parameters - Find correct timeout configuration
ModelSettingsパラメータ調査 - 正しいタイムアウト設定を見つける

This investigates the actual parameters available in ModelSettings.
ModelSettingsで使用可能な実際のパラメータを調査します。
"""

import os
import asyncio
from agents import Agent, Runner, RunConfig, ModelSettings


async def investigate_model_settings():
    """
    Investigate ModelSettings constructor parameters and attributes
    ModelSettingsコンストラクタのパラメータと属性を調査
    """
    print("🔍 Investigating ModelSettings Parameters")
    print("=" * 50)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: Check ModelSettings __init__ signature
    print("\n📋 Test 1: ModelSettings Constructor Signature")
    try:
        import inspect
        sig = inspect.signature(ModelSettings.__init__)
        print(f"   ModelSettings.__init__ parameters:")
        for param_name, param in sig.parameters.items():
            if param_name != 'self':
                print(f"     - {param_name}: {param}")
    except Exception as e:
        print(f"   ❌ Failed to get signature: {e}")
    
    # Test 2: Check ModelSettings class attributes/properties
    print("\n📋 Test 2: ModelSettings Class Attributes")
    try:
        model_settings = ModelSettings()
        print(f"   Available attributes:")
        attrs = [attr for attr in dir(model_settings) if not attr.startswith('_')]
        for attr in attrs:
            print(f"     - {attr}")
            
        # Check if any contain 'timeout'
        timeout_attrs = [attr for attr in attrs if 'timeout' in attr.lower()]
        if timeout_attrs:
            print(f"   Timeout-related attributes: {timeout_attrs}")
        else:
            print(f"   No timeout-related attributes found")
            
    except Exception as e:
        print(f"   ❌ Failed to create ModelSettings: {e}")
    
    # Test 3: Check if timeout can be set directly on ModelSettings
    print("\n📋 Test 3: Direct Timeout Setting on ModelSettings")
    timeout_params_to_test = [
        'timeout',
        'request_timeout', 
        'read_timeout',
        'connect_timeout',
        'total_timeout',
        'max_timeout',
        'api_timeout'
    ]
    
    for param in timeout_params_to_test:
        try:
            # Try setting directly as named parameter
            kwargs = {param: 120}
            model_settings = ModelSettings(**kwargs)
            print(f"   ✅ Success: ModelSettings({param}=120) works")
            
            # Test with agent
            agent = Agent(
                name="timeout_test",
                instructions="You are a helpful assistant.",
                model="gpt-4o-mini"
            )
            run_config = RunConfig(model_settings=model_settings)
            result = await Runner.run(agent, "Hi", run_config=run_config)
            print(f"      Agent execution successful: {result.final_output[:30]}...")
            break
            
        except TypeError as e:
            if 'unexpected keyword argument' in str(e):
                print(f"   ❌ {param}: Not a valid parameter")
            else:
                print(f"   ❌ {param}: {e}")
        except Exception as e:
            print(f"   ❌ {param}: {e}")
    
    # Test 4: Check RunConfig parameters  
    print("\n📋 Test 4: RunConfig Constructor Signature")
    try:
        sig = inspect.signature(RunConfig.__init__)
        print(f"   RunConfig.__init__ parameters:")
        for param_name, param in sig.parameters.items():
            if param_name != 'self':
                print(f"     - {param_name}: {param}")
                
        # Check if RunConfig has timeout parameter
        run_config_attrs = [attr for attr in dir(RunConfig) if not attr.startswith('_')]
        timeout_attrs = [attr for attr in run_config_attrs if 'timeout' in attr.lower()]
        if timeout_attrs:
            print(f"   RunConfig timeout-related attributes: {timeout_attrs}")
        else:
            print(f"   RunConfig has no timeout-related attributes")
            
    except Exception as e:
        print(f"   ❌ Failed to get RunConfig signature: {e}")
    
    # Test 5: Try setting timeout directly on RunConfig
    print("\n📋 Test 5: Direct Timeout Setting on RunConfig")
    try:
        run_config = RunConfig(timeout=120)
        print(f"   ✅ RunConfig(timeout=120) works")
        
        agent = Agent(
            name="timeout_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        result = await Runner.run(agent, "Hi", run_config=run_config)
        print(f"   Agent execution successful: {result.final_output[:30]}...")
        
    except TypeError as e:
        if 'unexpected keyword argument' in str(e):
            print(f"   ❌ timeout: Not a valid RunConfig parameter")
        else:
            print(f"   ❌ timeout: {e}")
    except Exception as e:
        print(f"   ❌ timeout: {e}")


if __name__ == "__main__":
    asyncio.run(investigate_model_settings())