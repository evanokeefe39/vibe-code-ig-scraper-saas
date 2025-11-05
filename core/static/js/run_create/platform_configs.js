// Platform configuration data for run creation form
const sourceTypeConfigs = {
    // YouTube source types
    'youtube-search': {
        name: 'YouTube Search',
        icon: '🔍',
        color: 'bg-red-100 text-red-800',
        template: 'youtube-search-template'
    },
    'youtube-channel': {
        name: 'YouTube Channel',
        icon: '📺',
        color: 'bg-red-100 text-red-800',
        template: 'youtube-channel-config-template'
    },
    'youtube-playlist': {
        name: 'YouTube Playlist',
        icon: '📋',
        color: 'bg-red-100 text-red-800',
        template: 'youtube-playlist-config-template'
    },
    'youtube-hashtag': {
        name: 'YouTube Hashtag',
        icon: '#️⃣',
        color: 'bg-red-100 text-red-800',
        template: 'youtube-hashtag-config-template'
    },
    'youtube-video': {
        name: 'YouTube Video',
        icon: '🎥',
        color: 'bg-red-100 text-red-800',
        template: 'youtube-video-config-template'
    },
    
    // Instagram source types
    'instagram-profile': {
        name: 'Instagram Profile',
        icon: '👤',
        color: 'bg-pink-100 text-pink-800',
        template: 'instagram-profile-template'
    },
    'instagram-post': {
        name: 'Instagram Post',
        icon: '📸',
        color: 'bg-pink-100 text-pink-800',
        template: 'instagram-post-config-template'
    },
    'instagram-hashtag': {
        name: 'Instagram Hashtag',
        icon: '#️⃣',
        color: 'bg-pink-100 text-pink-800',
        template: 'instagram-hashtag-config-template'
    },
    'instagram-search': {
        name: 'Instagram Search',
        icon: '🔍',
        color: 'bg-pink-100 text-pink-800',
        template: 'instagram-search-config-template'
    },
    
    // TikTok source types
    'tiktok-profile': {
        name: 'TikTok Profile',
        icon: '👤',
        color: 'bg-black text-white',
        template: 'tiktok-profile-template'
    },
    'tiktok-hashtag': {
        name: 'TikTok Hashtag',
        icon: '#️⃣',
        color: 'bg-black text-white',
        template: 'tiktok-hashtag-config-template'
    },
    'tiktok-search': {
        name: 'TikTok Search',
        icon: '🔍',
        color: 'bg-black text-white',
        template: 'tiktok-search-config-template'
    },
    'tiktok-video': {
        name: 'TikTok Video',
        icon: '🎥',
        color: 'bg-black text-white',
        template: 'tiktok-video-config-template'
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { sourceTypeConfigs };
} else {
    window.sourceTypeConfigs = sourceTypeConfigs;
}