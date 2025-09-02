// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { HomeComponent } from './home/home';
import { SingleVideoQuizzes } from './pages/single-video-quizzes/single-video-quizzes';

export const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent },
  // This route is where the user will be sent after the quiz is generated
  { path: 'quizzes/single-video', component: SingleVideoQuizzes },
  { path: '**', redirectTo: '/home' } 
];
