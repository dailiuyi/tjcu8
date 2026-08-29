const IMAGE_INDEX_VERSION = 1;
const IMAGE_RECORD_FIELDS = ['id', 'src', 'album', 'caption', 'alt'];

export function validateImageIndex(data) {
    if (!data || data.version !== IMAGE_INDEX_VERSION || !Array.isArray(data.images)) {
        throw new Error('图片索引数据契约不匹配');
    }

    data.images.forEach((image, index) => {
        IMAGE_RECORD_FIELDS.forEach(field => {
            if (typeof image[field] !== 'string' || image[field].length === 0) {
                throw new Error(`第 ${index + 1} 条图片记录缺少有效字段: ${field}`);
            }
        });

        if (!image.src.startsWith('../image/') || image.src.includes('\\')) {
            throw new Error(`第 ${index + 1} 条图片记录包含无效 URL: ${image.src}`);
        }
    });

    return data.images;
}

export async function loadImageIndex(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`图片索引请求失败: HTTP ${response.status}`);
    }

    return validateImageIndex(await response.json());
}
