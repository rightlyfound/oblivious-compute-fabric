#include <vulkan/vulkan.h>
#include <iostream>
#include <vector>
#include <cstring>
#include <algorithm>

struct OLEDeviceScore {
    VkPhysicalDevice device;
    VkPhysicalDeviceProperties props;
    uint32_t queue_family_idx;
};

bool compare_devices_deterministically(const OLEDeviceScore& a, const OLEDeviceScore& b) {
    if (a.props.deviceType != b.props.deviceType) return a.props.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU;
    if (a.props.vendorID != b.props.vendorID) return a.props.vendorID < b.props.vendorID;
    return a.props.deviceID < b.props.deviceID;
}

uint32_t find_compute_queue_family(VkPhysicalDevice device) {
    uint32_t count = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(device, &count, nullptr);
    std::vector<VkQueueFamilyProperties> families(count);
    vkGetPhysicalDeviceQueueFamilyProperties(device, &count, families.data());
    for (uint32_t i = 0; i < count; i++) {
        if (families[i].queueFlags & VK_QUEUE_COMPUTE_BIT) return i;
    }
    return -1;
}

int main() {
    std::cout << "[OLE CORE] Running bare-metal structural runtime discovery...\n";
    VkInstanceCreateInfo create_info = {};
    create_info.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;
    VkInstance instance;
    if (vkCreateInstance(&create_info, nullptr, &instance) != VK_SUCCESS) return 1;

    uint32_t dev_count = 0;
    vkEnumeratePhysicalDevices(instance, &dev_count, nullptr);
    std::vector<VkPhysicalDevice> physical_devices(dev_count);
    vkEnumeratePhysicalDevices(instance, &dev_count, physical_devices.data());

    std::vector<OLEDeviceScore> candidates;
    for (const auto& dev : physical_devices) {
        OLEDeviceScore score;
        score.device = dev;
        vkGetPhysicalDeviceProperties(dev, &score.props);
        score.queue_family_idx = find_compute_queue_family(dev);
        if (score.queue_family_idx != -1) candidates.push_back(score);
    }
    std::sort(candidates.begin(), candidates.end(), compare_devices_deterministically);
    
    if(candidates.empty()) {
        std::cerr << "[FATAL] No validated hardware execution boundaries detected.\n";
        return 1;
    }
    std::cout << "[OLE CORE] Binding hardware resource substrate: " << candidates.front().props.deviceName << "\n";
    
    vkDestroyInstance(instance, nullptr);
    return 0;
}
