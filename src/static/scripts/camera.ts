// フラッシュエフェクトの制御
export function showFlash(): void {
    const flash = document.querySelector('.flash');
    if (flash) {
        flash.classList.add('active');
        setTimeout(() => flash.classList.remove('active'), 150);
    }
}

// キャプチャ処理
export async function captureImage(): Promise<void> {
    try {
        showFlash();
        const response = await fetch('/capture', {
            method: 'POST'
        });
        const data = await response.json();
        
        const statusElement = document.querySelector('.status');
        if (!statusElement) {
            throw new Error('Status element not found');
        }

        if (data.status === 'success') {
            statusElement.textContent = `キャプチャ成功: ${data.filename}`;
        } else {
            statusElement.textContent = 'キャプチャに失敗しました';
        }
    } catch (error) {
        console.error('キャプチャエラー:', error);
        const statusElement = document.querySelector('.status');
        if (statusElement) {
            statusElement.textContent = 'キャプチャ中にエラーが発生しました';
        }
    }
}