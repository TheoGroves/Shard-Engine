extern "C" {
    // Find best NVIDIA GPU
    __declspec(dllexport) unsigned long NvOptimusEnablement = 0x00000001;
    
    // Find best AMD GPU
    __declspec(dllexport) int AmdPowerXpressRequestHighPerformance = 1;
}
