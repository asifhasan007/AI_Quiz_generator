// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { HomeComponent } from './home/home';
import { SingleVideoQuizzes } from './pages/single-video-quizzes/single-video-quizzes';
import { PdfQuizzes } from './pages/pdf-quizzes/pdf-quizzes';
import { MultipleVideosQuizzes } from './pages/multiple-videos-quizzes/multiple-videos-quizzes';
import { AllQuizzes } from './pages/all-quizzes/all-quizzes';
import { AllQuizzes } from './pages/all-quizzes/all-quizzes';
export const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent },
 
  // Route for video quiz results
  { path: 'quizzes/single-video', component: SingleVideoQuizzes },
 
  // Route for PDF quiz results
  { path: 'quizzes/pdf', component: PdfQuizzes },
 
  { path: 'quizzes/multiple-videos-quizzes', component: MultipleVideosQuizzes },
 
  // ✅ Place this before wildcard
  { path: 'all-quizzes', component: AllQuizzes },
 
  // Wildcard route to redirect any unknown paths to home
  { path: '**', redirectTo: '/home' }
];
 
 