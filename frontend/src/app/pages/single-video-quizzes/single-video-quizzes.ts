import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-single-video-quizzes',
  standalone: true,
  imports: [
    CommonModule, // Required for *ngIf, *ngFor
    FormsModule   // Required for [(ngModel)]
  ],
  templateUrl: './single-video-quizzes.html',
  styleUrls: ['./single-video-quizzes.css']
})
export class SingleVideoQuizzes implements OnInit {
  // This array will hold the quiz data (questions, options, answers)
  quiz: any[] = [];
  // This object will store the user's selected answer for each question
  userAnswers: { [key: number]: string } = {};
  // A flag to check if the user has submitted the quiz for grading
  isSubmitted: boolean = false;

  constructor(private router: Router) {
    // Access the navigation state to get the data passed from the home component
    const navigation = this.router.getCurrentNavigation();
    const state = navigation?.extras.state as { quiz: any[] };
    
    // If quiz data exists in the state, assign it to the local quiz property
    if (state?.quiz) {
      this.quiz = state.quiz;
    }
  }

  ngOnInit(): void {
    // This is a safeguard. If the user accesses this page directly (e.g., by refreshing),
    // the state will be lost, so we redirect them back to the home page.
    if (!this.quiz || this.quiz.length === 0) {
      this.router.navigate(['/home']);
    }
  }

  /**
   * This method is called when the user clicks the "Check Answers" button.
   * It sets the isSubmitted flag to true, which triggers the UI to show results.
   */
  submitQuiz(): void {
    this.isSubmitted = true;
    window.scrollTo(0, 0); // Scroll to the top of the page to show the score
  }

  /**
   * Calculates the user's score after submission.
   * @returns The total number of correct answers.
   */
  getScore(): number {
    if (!this.isSubmitted) return 0;
    // It iterates through the quiz and compares the correct answer with the user's answer
    return this.quiz.reduce((score, question, index) => {
      if (question.answer === this.userAnswers[index]) {
        return score + 1;
      }
      return score;
    }, 0);
  }

  /**
   * Navigates the user back to the home page to start a new quiz.
   */
  startNewQuiz(): void {
    this.router.navigate(['/home']);
  }
}
