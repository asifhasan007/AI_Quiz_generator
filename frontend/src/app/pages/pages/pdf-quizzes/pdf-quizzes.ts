import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-pdf-quizzes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './pdf-quizzes.html',
  styleUrls: ['./pdf-quizzes.css']
})
export class PdfQuizzes implements OnInit {
  quiz: any[] = [];
  userAnswers: string[] = [];
  isSubmitted = false;
  
  constructor(private router: Router) {
  }

  ngOnInit(): void {
   
    const state = history.state as { quiz?: any[] };

    if (state?.quiz && Array.isArray(state.quiz) && state.quiz.length > 0) {
      console.log("Quiz data received:", state.quiz);
      this.quiz = state.quiz;
      this.userAnswers = new Array(this.quiz.length).fill('');
    } else {
      console.error("No quiz data found in navigation state.");
      this.quiz = []; 
    }
  }

  submitQuiz(): void {
    this.isSubmitted = true;
  }

  getScore(): number {
    return this.quiz.reduce((score, question, index) => {
      return score + (this.userAnswers[index] === question.answer ? 1 : 0);
    }, 0);
  }

  startNewQuiz(): void {
    this.router.navigate(['/']); 
  }
}
