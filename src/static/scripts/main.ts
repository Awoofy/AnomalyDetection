import { captureImage } from './camera';

// スペースキーの検出
document.addEventListener('keydown', (event: KeyboardEvent) => {
    if (event.code === 'Space' && !event.repeat) {
        event.preventDefault();  // スクロール防止
        captureImage();
    }
});

// キャプチャボタンのクリックイベントを設定
document.addEventListener('DOMContentLoaded', () => {
    const captureButton = document.querySelector('.capture-button');
    if (captureButton) {
        captureButton.addEventListener('click', () => {
            captureImage();
        });
    }
});