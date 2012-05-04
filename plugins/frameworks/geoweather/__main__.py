import location, weather, astronomy

modules = [location, weather, astronomy]

for module in modules:
    print '================= Testing', `module.__name__`, 'module ================='
    module._test_module()
    print
