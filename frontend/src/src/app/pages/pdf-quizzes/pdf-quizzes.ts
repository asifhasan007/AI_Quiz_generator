import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

// 1. Import the necessary services
import { ApiService } from '../../services/api';
import { QuizStateService } from '../../services/quiz-state.service';

@Component({
  selector: 'app-pdf-quizzes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './pdf-quizzes.html',
  styleUrls: ['./pdf-quizzes.css']
})
export class PdfQuizzes implements OnInit {
  quiz: any[] = [];
  // Add properties for source and loading state
  source: string = 'Unknown Source';
  isLoading: boolean = false;
  
  constructor(
    private router: Router,
    // 2. Inject the services
    private apiService: ApiService,
    private quizStateService: QuizStateService
  ) {
    const state = history.state as { quiz?: any[], source?: string };
    if (state) {
      this.quiz = state.quiz || [];
      this.source = state.source || 'Unknown PDF';
    }
  }

  ngOnInit(): void {
    if (!this.quiz || this.quiz.length === 0) {
      this.goBackToHome();
    }
  }

  goBackToHome(): void {
    this.router.navigate(['/home']); 
  }

  /**
   * 3. New method to handle quiz regeneration for PDFs
   */
  regenerateQuiz(): void {
    const fileToRegenerate = this.quizStateService.lastUploadedFile;

    if (!fileToRegenerate) {
      alert('Could not find the original file to regenerate. Please go back and upload it again.');
      return;
    }

    this.isLoading = true;
    this.quiz = [];

    const formData = new FormData();
    formData.append('file', fileToRegenerate, fileToRegenerate.name);

    this.apiService.generateQuizFromPdf(formData).subscribe({
      next: (response: any[]) => {
        const newQuizData = response[0]?.quiz_data;

        if (newQuizData) {
          this.quiz = newQuizData;
          // Update the quiz in the shared state service
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
    if (correctIndex !== -1) {
      return this.getOptionLetter(correctIndex);
    }
    
    return question.answer;
  }
}
