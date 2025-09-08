import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) {}

  // Handles video URLs
  generateQuizFromVideo(videoUrl: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/generate-quiz`, { video_url: videoUrl });
  }

  // Handles PDF file uploads
  generateQuizFromPdf(formData: FormData): Observable<any> {
    return this.http.post(`${this.baseUrl}/generate-quiz`, formData);
  }

  // New method for single local video paths
  generateQuizFromVideoWithOsPath(osVideoPath: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/generate-quiz`, { os_video_path: osVideoPath });
  }

  // New method for multiple local video paths (joined as a string)
  generateQuizFromMultipleOsPaths(osVideoPaths: string[]): Observable<any> {
    return this.http.post(`${this.baseUrl}/generate-quiz`, { os_video_path: osVideoPaths.join(',') });
  }
}
