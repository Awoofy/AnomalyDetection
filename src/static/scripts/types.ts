export interface CameraDevice {
    name: string;
    path: string;
}

export interface ApiResponse {
    devices: CameraDevice[];
}