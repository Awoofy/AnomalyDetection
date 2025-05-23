import { CameraDevice, ApiResponse, Resolution, ResolutionsApiResponse } from './types';

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

// カメラ選択機能
export class CameraSelector {
    private selectElement: HTMLSelectElement;
    private statusElement: HTMLDivElement;
    private resolutionSelector: ResolutionSelector; // ResolutionSelectorのインスタンスを保持

    constructor(resolutionSelector: ResolutionSelector) {
        this.selectElement = document.getElementById('camera-select') as HTMLSelectElement;
        this.statusElement = document.getElementById('camera-status') as HTMLDivElement;
        this.resolutionSelector = resolutionSelector; // インスタンスを保存
        
        this.init();
    }

    private async init() {
        try {
            // カメラデバイス一覧の取得
            const response = await fetch('/api/cameras');
            const data: ApiResponse = await response.json();
            
            // プルダウンメニューの作成
            this.selectElement.innerHTML = `
                <option value="">カメラを選択してください</option>
                ${data.devices.map(device => `
                    <option value="${device.path}">${device.name}</option>
                `).join('')}
            `;
            
            // イベントリスナーの設定
            this.selectElement.addEventListener('change', () => this.onCameraSelect());
        } catch (error) {
            this.showError('カメラ一覧の取得に失敗しました');
        }
    }

    private async onCameraSelect() {
        const selectedPath = this.selectElement.value;
        if (!selectedPath) return;

        try {
            this.showStatus('カメラを切り替え中...');
            
            // カメラの切り替え
            const response = await fetch('/api/camera/select', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ device_path: selectedPath })
            });
            
            if (!response.ok) throw new Error('カメラの切り替えに失敗しました');
            
            // ストリームの再読み込み
            const videoElement = document.querySelector('.video-container img') as HTMLImageElement;
            if (videoElement) {
                videoElement.src = `/video_feed?t=${Date.now()}`;
            }
            
            this.showStatus('カメラを切り替えました');
            // 解像度リストを更新
            if (this.resolutionSelector) {
                await this.resolutionSelector.loadResolutions();
            }
        } catch (error) {
            this.showError('カメラの切り替えに失敗しました');
        }
    }

    private showStatus(message: string) {
        this.statusElement.textContent = message;
        this.statusElement.className = 'status';
    }

    private showError(message: string) {
        this.statusElement.textContent = message;
        this.statusElement.className = 'status error';
    }
}

// 解像度選択機能
export class ResolutionSelector {
    private selectElement: HTMLSelectElement;
    private statusElement: HTMLDivElement;

    constructor() {
        this.selectElement = document.getElementById('resolution-select') as HTMLSelectElement;
        this.statusElement = document.getElementById('resolution-status') as HTMLDivElement;

        this.loadResolutions(); // 初期化時に解像度を読み込む
    }

    public async loadResolutions(): Promise<void> { // publicメソッドに変更し、initから名前変更
        try {
            this.selectElement.innerHTML = '<option value="">解像度を読み込み中...</option>'; // 読み込み中表示
            // 解像度一覧の取得
            const response = await fetch('/api/camera/resolutions');
            const data: ResolutionsApiResponse = await response.json();

            // プルダウンメニューの作成
            this.selectElement.innerHTML = `
                <option value="">解像度を選択してください</option>
                ${data.resolutions.map(res => `
                    <option value="${res.width}x${res.height}">${res.width}x${res.height}</option>
                `).join('')}
            `;

            // イベントリスナーの設定
            this.selectElement.addEventListener('change', () => this.onResolutionSelect());
        } catch (error) {
            this.showError('解像度一覧の取得に失敗しました');
        }
    }

    private async onResolutionSelect() {
        const selectedResolution = this.selectElement.value;
        if (!selectedResolution) return;

        const [width, height] = selectedResolution.split('x').map(Number);

        try {
            this.showStatus('解像度を切り替え中...');

            // 解像度の設定
            const response = await fetch('/api/camera/resolution', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ width, height })
            });

            if (!response.ok) throw new Error('解像度の設定に失敗しました');

            this.showStatus('解像度を設定しました');
        } catch (error) {
            this.showError('解像度の設定に失敗しました');
        }
    }

    private showStatus(message: string) {
        this.statusElement.textContent = message;
        this.statusElement.className = 'status';
    }

    private showError(message: string) {
        this.statusElement.textContent = message;
        this.statusElement.className = 'status error';
    }
}

// カメラ選択機能と解像度選択機能の初期化
const resolutionSelector = new ResolutionSelector();
new CameraSelector(resolutionSelector);