import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

// ✅ 1. Import services
import { ApiService } from '../../services/api';
import { QuizStateService } from '../../services/quiz-state.service';

@Component({
  selector: 'app-single-video-quizzes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './single-video-quizzes.html',
  styleUrls: ['./single-video-quizzes.css']
})
export class SingleVideoQuizzes implements OnInit {
  quiz: any[] = [];
  // ✅ Add properties for source and loading state
  source: string = 'Unknown Source';
  isLoading: boolean = false;

  constructor(
    private router: Router,
    // ✅ 2. Inject the services
    private apiService: ApiService,
    private quizStateService: QuizStateService
  ) {
    const navigation = this.router.getCurrentNavigation();
    // ✅ Update to get both quiz and source
    const state = navigation?.extras.state as { quiz: any[], source: string };
    
    if (state) {
      this.quiz = state.quiz || [];
      this.source = state.source || 'Unknown Source';
    }
  }

  ngOnInit(): void {
    if (!this.quiz || this.quiz.length === 0) {
      this.router.navigate(['/home']);
    }
  }

  goBackToHome(): void {
    this.router.navigate(['/home']);
  }
  
  /**
   * ✅ 3. New method to handle quiz regeneration
   */
  regenerateQuiz(): void {
    this.isLoading = true;
    this.quiz = [];

    this.apiService.generateQuizFromVideo(this.source).subscribe({
      next: (response: any[]) => {
        const newQuizData = response[0]?.quiz_data;

        if (newQuizData) {
          this.quiz = newQuizData;
          const itemIndex = this.quizStateService.generatedItems.findIndex(
            item => item.source === this.source
          );
          if (itemIndex > -1) {
            this.quizStateService.generatedItems[itemIndex].quiz = newQuizData;
          }
        } else {
          alert('Failed to regenerate the quiz.');
        }
        this.isLoading = false;
      },
      error: (err) => {
        this.isLoading = false;
        alert(`An error occurred: ${err.error?.error || 'Unknown error'}`);
      }
    });
  }

  // --- Helper methods remain unchanged ---
  getOptionLetter(index: number): string {
    return String.fromCharCode(65 + index);
  }

  getCorrectAnswerLetter(question: any): string {
    if (question.type === 'True/False') {
      return question.answer === 'True' ? 'A' : 'B';
    }
    const correctIndex = question.options.findIndex((opt: string) => opt === question.answer);
    return correctIndex !== -1 ? this.getOptionLetter(correctIndex) : question.answer;
  }
}
