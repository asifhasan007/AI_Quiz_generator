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
  singleVideoLink: string = '';
  selectedFile: File | null = null;
  selectedFileName: string | null = null;
  
  isLoading: boolean = false;
  errorMessage: string | null = null;
  
  isStarted: boolean = true;
  selectedOption: 'single' | 'pdf' = 'single';

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  // --- Main Submit Handler ---
  submit(): void {
    if (this.selectedOption === 'single') {
      this.submitLink();
    } else if (this.selectedOption === 'pdf') {
      this.submitPdf();
    }
  }

  // --- Video Submission Logic ---
  private submitLink(): void {
    if (!this.singleVideoLink || !this.singleVideoLink.trim()) {
      this.errorMessage = "Please enter a valid video link.";
      return;
    }

    this.isLoading = true;
    this.errorMessage = null;
    console.log("Sending URL to backend:", this.singleVideoLink);

    this.apiService.generateQuizFromVideo(this.singleVideoLink.trim()).subscribe({
      next: (response) => {
        this.isLoading = false;
        console.log('Quiz generated successfully!', response);
        this.router.navigate(['/quizzes/single-video'], { state: { quiz: response } });
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = `Error: ${err.error?.error || 'Failed to generate quiz.'}`;
        console.error('An error occurred:', err);
      }
    });
  }

  // --- PDF Submission Logic ---
  private submitPdf(): void {
    if (!this.selectedFile) {
      this.errorMessage = "Please select a PDF file.";
      return;
    }
   
    this.isLoading = true;
    this.errorMessage = null;

    const formData = new FormData();
    formData.append('file', this.selectedFile, this.selectedFile.name);

    console.log("Uploading PDF to backend:", this.selectedFile.name);
    this.apiService.generateQuizFromPdf(formData).subscribe({
      next: (response) => {
        this.isLoading = false;
        console.log('PDF Quiz generated successfully!', response);
        // Navigate to the new PDF quiz results page
        this.router.navigate(['/quizzes/pdf'], { state: { quiz: response } });
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = `Error: ${err.error?.error || 'Failed to generate quiz from PDF.'}`;
        console.error('An error occurred:', err);
      }
    });
  }
  
  // --- UI Helper Methods ---
  goBack(): void {
    this.isStarted = false;
    this.selectedOption = 'single';
  }

  selectOption(option: 'single' | 'pdf'): void {
    this.selectedOption = option;
    this.errorMessage = null; // Clear errors when switching
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      if (file.type === "application/pdf") {
        this.selectedFile = file;
        this.selectedFileName = file.name;
        this.errorMessage = null;
      } else {
        this.errorMessage = "Invalid file type. Please upload a PDF.";
        this.selectedFile = null;
        this.selectedFileName = null;
      }
    }
  }
}
