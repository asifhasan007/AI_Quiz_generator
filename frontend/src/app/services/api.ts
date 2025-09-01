import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  // The full URL to your backend endpoint
  private apiUrl = 'http://127.0.0.1:5000/api/generate-quiz';

  constructor(private http: HttpClient) { }

  /**
   * Sends a video URL to the backend to generate a quiz.
   * @param videoUrl The URL of the video to be processed.
   * @returns An Observable with the quiz data from the backend.
   */
  generateQuiz(videoUrl: string): Observable<any> {
    // Create the exact payload the backend expects: { "video_url": "..." }
    const payload = { video_url: videoUrl };
    
    // Send the POST request
    return this.http.post<any>(this.apiUrl, payload);
  }
}
