// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { HomeComponent } from './home/home'; 
import { SingleVideoQuizzes } from './pages/single-video-quizzes/single-video-quizzes'; 
import { PdfQuizzes } from './pages/pdf-quizzes/pdf-quizzes'; 

export const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent },
  
  // Route for video quiz results
  { path: 'quizzes/single-video', component: SingleVideoQuizzes },
  
  // Route for PDF quiz results
  { path: 'quizzes/pdf', component: PdfQuizzes },
  
  // Wildcard route to redirect any unknown paths to home
  { path: '**', redirectTo: '/home' } 
];
