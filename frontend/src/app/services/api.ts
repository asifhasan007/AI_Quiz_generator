import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) {}

  // Renamed for clarity, was generateQuiz
  generateQuizFromVideo(videoUrl: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/generate-quiz`, { video_url: videoUrl });
  }

  // New method for PDF uploads
  generateQuizFromPdf(formData: FormData): Observable<any> {
    // HttpClient will automatically set the 'Content-Type' to 'multipart/form-data'
    return this.http.post(`${this.baseUrl}/generate-quiz`, formData);
  }
}
