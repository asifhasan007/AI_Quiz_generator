import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

// ✅ 1. Import the necessary services
import { ApiService } from '../../services/api'; 
import { QuizStateService } from '../../services/quiz-state.service';

@Component({
  selector: 'app-multiple-videos-quizzes',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './multiple-videos-quizzes.html',
  styleUrls: ['./multiple-videos-quizzes.css']
})
export class MultipleVideosQuizzes implements OnInit {
  quiz: any[] = [];
  source: string = 'Unknown Source';
  isLoading: boolean = false; // For the loading indicator

  constructor(
    private router: Router,
    // ✅ 2. Inject the services
    private apiService: ApiService,
    private quizStateService: QuizStateService
  ) {
    const nav = this.router.getCurrentNavigation();
    const state = nav?.extras?.state as { quiz: any[], source: string };
    if (state) {
      this.quiz = state.quiz || [];
      this.source = state.source || 'Unknown Source';
    }
  }

  ngOnInit(): void {
    if (this.quiz.length === 0) {
      this.goBackToHome();
    }
  }

  goBackToHome(): void {
    this.router.navigate(['/home']);
  }
  
  /**
   * ✅ 3. New method to handle quiz regeneration
   */
  regenerateQuiz(): void {
    this.isLoading = true; // Show loading spinner
    this.quiz = []; // Clear the current quiz to show the loading message

    this.apiService.generateQuizFromVideo(this.source).subscribe({
      next: (response: any[]) => {
        // The API returns an array, but for a single link, it will have one item.
        const newQuizData = response[0]?.quiz_data;

        if (newQuizData) {
          // Update the quiz on this page immediately
          this.quiz = newQuizData;

          // Find and update the quiz in the shared state service
          const itemIndex = this.quizStateService.generatedItems.findIndex(
            item => item.source === this.source
          );
          if (itemIndex > -1) {
            this.quizStateService.generatedItems[itemIndex].quiz = newQuizData;
          }
        } else {
          // Handle case where regeneration fails
          alert('Failed to regenerate the quiz. Please try again.');
        }
        
        this.isLoading = false; // Hide loading spinner
      },
      error: (err) => {
        this.isLoading = false;
        alert(`An error occurred: ${err.error?.error || 'Unknown error'}`);
      }
    });
  }

  // --- Helper methods (getOptionLetter, getCorrectAnswerLetter) remain unchanged ---
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
