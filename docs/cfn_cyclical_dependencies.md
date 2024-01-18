# Cyclical Dependencies 

Probably one of the most annoying issues to have since it's not clearly apparent what needs to change or get fixed. But in cases of cyclical dependencies, try testing `cdk ls` with one stack instantiation at a time. 

Example 1: 

`RuntimeError: Error: 'BaseStack' depends on 'EksStack'`

This is due to the another stack using something like `base_stack.get_vpc` in an `AlbStack` (3rd stack) instead of getting the vpc and subnets from the parent stack. 

AlbStack's parent stack is EksStack since AlbStack depends on EksStack. 

