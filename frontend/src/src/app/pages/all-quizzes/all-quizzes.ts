import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { QuizStorageService } from '../../services/quiz-storage.service';

@Component({
  selector: 'app-all-quizzes',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './all-quizzes.html',
  styleUrls: ['./all-quizzes.css']
})
export class AllQuizzes implements OnInit {
  allQuizzes: any[] = [];
  isLoading: boolean = true;

  constructor(
    private quizStorageService: QuizStorageService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadQuizzes();
  }

  async loadQuizzes(): Promise<void> {
    try {
      this.allQuizzes = (await this.quizStorageService.getAllQuizzes()).reverse();
      console.log("Loaded quizzes:", this.allQuizzes);
    } catch (error) {
      console.error("Failed to load quizzes from IndexedDB", error);
    } finally {
      this.isLoading = false;
    }
  }

  viewQuiz(item: any): void {
    let targetRoute: string;
    if (item.type === 'pdf') {
      targetRoute = '/quizzes/pdf';
    } else if (item.type === 'video') {
      targetRoute = item.submissionType === 'multiple' ? '/quizzes/multiple-videos-quizzes' : '/quizzes/single-video';
    } else {
      return;
    }
    this.router.navigate([targetRoute], { state: { quiz: item.quiz, source: item.source } });
  }

  downloadQuiz(item: any): void {
    if (!item.source) {
      alert('Could not download quiz. Source name is missing.');
      return;
    }
    const quizText = this.parseQuizToText(item.quiz);
    if (!quizText) {
      alert('Could not download quiz. The data might be empty or invalid.');
      return;
    }

    const blob = new Blob([quizText], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const safeSourceName = item.source.replace(/[^a-z0-9]/gi, '_').slice(0, 50);
    a.download = `${safeSourceName}_quiz.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  private parseQuizToText(quizData: any[]): string {
    if (!quizData || !Array.isArray(quizData)) return '';
    let formattedText = '';
    const toLetter = (index: number) => String.fromCharCode(65 + index);

    const mcqs = quizData.filter(q => q.type === 'Multiple Choice');
    const trueFalse = quizData.filter(q => q.type === 'True/False');

    if (mcqs.length > 0) {
      formattedText += 'Multiple Choice Questions\n\n';
      mcqs.forEach((question) => {
        formattedText += `${question.question}\n`;
        let correctOptionLetter = '';
        if (question.options && Array.isArray(question.options)) {
          question.options.forEach((option: string, optIndex: number) => {
            const optionLetter = toLetter(optIndex);
            formattedText += `${optionLetter}. ${option}\n`;
            if (option === question.answer) {
              correctOptionLetter = optionLetter;
            }
          });
        }
        formattedText += `ANSWER: ${correctOptionLetter}\n\n`;
      });
    }

    if (trueFalse.length > 0) {
      formattedText += '\n--- TRUE/FALSE ---\n\n';
      trueFalse.forEach((question) => {
        formattedText += `${question.question}\n`;
        formattedText += `A. True\nB. False\n`;
        const correctAnswer = question.answer === 'True' ? 'A' : 'B';
        formattedText += `ANSWER: ${correctAnswer}\n\n`;
      });
    }

    return formattedText.trim();
  }

  async deleteQuiz(id: number): Promise<void> {
    try {
      await this.quizStorageService.deleteQuiz(id);
      this.allQuizzes = this.allQuizzes.filter(q => q.id !== id);
    } catch (error) {
      console.error("Failed to delete quiz", error);
    }
  }

  goHome(): void {
    this.router.navigate(['/']);
  }
}
