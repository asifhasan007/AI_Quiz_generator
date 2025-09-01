import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../services/api'; // Ensure this path is correct

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './home.html',
  styleUrls: ['./home.css']
})
export class HomeComponent {
  // --- Component State Properties ---
  
  // This property holds the video link from the input field
  singleVideoLink: string = '';
  
  // These properties manage the UI during the API call
  isLoading: boolean = false;
  errorMessage: string | null = null;
  
  // These properties are for managing different views within the component (optional)
  isStarted: boolean = true;
  selectedOption: 'single' | null = 'single';

  /**
   * The constructor injects the necessary services:
   * - ApiService: To communicate with the backend.
   * - Router: To navigate to another page after the API call.
   */
  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  /**
   * This is the primary function called when the user clicks the "Submit" button.
   */
  submitLink(): void {
    // 1. Validate the user's input to ensure it's not empty.
    if (!this.singleVideoLink || !this.singleVideoLink.trim()) {
      this.errorMessage = "Please enter a valid video link.";
      return;
    }

    // 2. Set the loading state to provide feedback to the user.
    this.isLoading = true;
    this.errorMessage = null;

    // 3. Log the action for debugging purposes.
    console.log("Sending URL to backend:", this.singleVideoLink);

    // 4. Call the generateQuiz method from the ApiService.
    this.apiService.generateQuiz(this.singleVideoLink.trim()).subscribe({
      // The 'next' block runs if the API call is successful
      next: (response) => {
        this.isLoading = false; // Turn off loading indicator
        console.log('Quiz generated successfully!', response);
        
        // 5. Navigate to the quiz results page.
        // The 'state' object carries the quiz data to the next component.
        this.router.navigate(['/quizzes/single-video'], { state: { quiz: response } });
      },
      // The 'error' block runs if the API call fails
      error: (err) => {
        this.isLoading = false; // Turn off loading indicator
        // Display a user-friendly error message.
        this.errorMessage = `Error: ${err.error?.error || 'Failed to generate quiz.'}`;
        console.error('An error occurred:', err);
      }
    });
  }

  // --- Optional helper methods for more complex UI ---

  /**
   * Example function to go back to a previous view state.
   */
  goBack(): void {
    this.isStarted = false;
    this.selectedOption = null;
  }
  
  /**
   * Example function to handle option selection if you have multiple options.
   */
  selectOption(option: 'single'): void {
    this.selectedOption = option;
  }
}
