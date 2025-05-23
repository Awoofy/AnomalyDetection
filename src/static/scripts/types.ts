export interface CameraDevice {
    name: string;
    path: string;
}

export interface ApiResponse {
    devices: CameraDevice[];
}

export interface Resolution {
    width: number;
    height: number;
}

export interface ResolutionsApiResponse {
    resolutions: Resolution[];
}