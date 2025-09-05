import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../services/api';
import { QuizStateService } from '../services/quiz-state.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './home.html',
  styleUrls: ['./home.css']
})
export class HomeComponent implements OnInit {
  singleVideoLink: string = '';
  selectedFile: File | null = null;
  selectedFileName: string | null = null;
  isLoading: boolean = false;
  errorMessage: string | null = null;
  isStarted: boolean = true;
  selectedOption: 'single' | 'pdf' = 'single';
  quizGenerated: boolean = false;
  generatedItems: any[] = [];
  
  // Properties for the fake progress bar
  progress: number = 0;
  progressMessage: string = "Starting...";
  private progressInterval: any = null;

  constructor(
    private apiService: ApiService,
    private router: Router,
    private quizStateService: QuizStateService
  ) {}

  ngOnInit(): void {
    this.generatedItems = this.quizStateService.generatedItems;
    this.quizGenerated = this.quizStateService.quizGenerated;
  }

  // Method to start the fake progress simulation
  private startFakeProgress(): void {
    this.progress = 0;
    this.isLoading = true;
    this.progressMessage = "Starting quiz generation...";
    const phases = [
      { end: 25, message: "Analyzing content..." },
      { end: 65, message: "Extracting key points..." },
      { end: 85, message: "Generating questions..." },
      { end: 95, message: "Finalizing quiz..." }
    ];
    let currentPhase = 0;
    this.progressInterval = setInterval(() => {
      if (currentPhase < phases.length) {
        if (this.progress < phases[currentPhase].end) {
          this.progress++;
          this.progressMessage = phases[currentPhase].message;
        } else {
          currentPhase++;
        }
      } else {
        this.progressMessage = "Almost done...";
        clearInterval(this.progressInterval);
      }
    }, 1500);
  }

  // Method to finalize the progress
  private completeProgress(): void {
    if (this.progressInterval) {
      clearInterval(this.progressInterval);
    }
    this.progress = 100;
    this.progressMessage = "Quiz generated successfully!";
    setTimeout(() => {
      this.isLoading = false;
      this.ngOnInit(); // Refresh state to show table
    }, 1000);
  }

  // Updated main submit function
  submit(): void {
    this.quizStateService.clearState();
    this.generatedItems = [];
    this.startFakeProgress(); // Start the progress bar
    if (this.selectedOption === 'single') {
      this.submitLink();
    } else if (this.selectedOption === 'pdf') {
      this.submitPdf();
    }
  }

  private submitLink(): void {
    const links = this.singleVideoLink.trim();
    if (!links) {
      this.errorMessage = "Please enter one or more valid video links or paths.";
      this.isLoading = false;
      clearInterval(this.progressInterval);
      return;
    }

    const isLocalPath = (str: string) => /^([a-zA-Z]:\\|\/)/.test(str.trim());
    const linkArray = links.split(/[\n,]+/).map(link => link.trim()).filter(link => link);
    const submissionType = linkArray.length > 1 ? 'multiple' : 'single';
    this.errorMessage = null;

    const handleSuccess = (response: any[]) => {
        this.completeProgress();
        const newItems: any[] = [];
        response.forEach(result => {
            newItems.push({
                source: result.source_name || result.source, // **FIX: Check for both properties**
                type: 'video',
                quiz: result.quiz_data,
                error: result.error,
                submissionType: submissionType
            });
        });
        this.quizStateService.addItems(newItems);
        this.singleVideoLink = '';
    };

    const handleError = (err: any, context: string) => {
        this.isLoading = false;
        clearInterval(this.progressInterval);
        this.errorMessage = `Error: ${err.error?.error || 'Failed to generate quiz from ' + context + '.'}`;
    };

    if (linkArray.length > 0 && isLocalPath(linkArray[0])) {
        const apiCall = linkArray.length === 1 
            ? this.apiService.generateQuizFromVideoWithOsPath(linkArray[0])
            : this.apiService.generateQuizFromMultipleOsPaths(linkArray);
        
        apiCall.subscribe({
            next: handleSuccess,
            error: (err) => handleError(err, 'local video')
        });
    } else {
        const urlString = linkArray.join(',');
        this.apiService.generateQuizFromVideo(urlString).subscribe({
            next: handleSuccess,
            error: (err) => handleError(err, 'URL')
        });
    }
  }

  private submitPdf(): void {
    if (!this.selectedFile) {
      this.errorMessage = "Please select a PDF file.";
      this.isLoading = false;
      clearInterval(this.progressInterval);
      return;
    }
    this.quizStateService.setLastUploadedFile(this.selectedFile);
    this.errorMessage = null;
    const formData = new FormData();
    formData.append('file', this.selectedFile, this.selectedFile.name);

    this.apiService.generateQuizFromPdf(formData).subscribe({
      next: (response: any[]) => {
        this.completeProgress();
        const newItems: any[] = [];
        response.forEach(result => {
          newItems.push({
            source: result.source_name || result.source, // **FIX: Check for both properties**
            type: 'pdf',
            quiz: result.quiz_data,
            error: result.error
          });
        });
        this.quizStateService.addItems(newItems);
      },
      error: (err) => {
        this.isLoading = false;
        clearInterval(this.progressInterval);
        this.errorMessage = `Error: ${err.error?.error || 'Failed to generate quiz from PDF.'}`;
      }
    });
  }
  
  viewQuiz(item: any): void {
    let targetRoute: string;
    if (item.type === 'pdf') {
      targetRoute = '/quizzes/pdf';
    } else if (item.type === 'video') {
      if (item.submissionType === 'multiple') {
        targetRoute = '/quizzes/multiple-videos-quizzes';
      } else {
        targetRoute = '/quizzes/single-video';
      }
    } else {
      return;
    }
    this.router.navigate([targetRoute], { state: { quiz: item.quiz, source: item.source } });
  }
  
  goBack(): void {
    this.quizStateService.clearState();
    this.ngOnInit();
    this.errorMessage = null;
    this.singleVideoLink = '';
    this.selectedFile = null;
    this.selectedFileName = null;
  }

  downloadQuiz(item: any): void {
    // This function will now work because item.source is guaranteed to be a string
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
    if (!quizData || !Array.isArray(quizData)) {
      return '';
    }
    let formattedText = '';
    const toLetter = (index: number) => String.fromCharCode(65 + index);
    const mcqs = quizData.filter(q => q.type === 'Multiple Choice');
    const trueFalse = quizData.filter(q => q.type === 'True/False');

    mcqs.forEach((question, index) => {
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

    if (mcqs.length > 0 && trueFalse.length > 0) {
      formattedText += '\n';
    }

    trueFalse.forEach((question, index) => {
      formattedText += `${question.question}\n`;
      formattedText += `A. True\nB. False\n`;
      const correctAnswer = question.answer === 'True' ? 'A' : 'B';
      formattedText += `ANSWER: ${correctAnswer}\n\n`;
    });

    return formattedText.trim();
  }

  selectOption(option: 'single' | 'pdf'): void {
    this.selectedOption = option;
    this.errorMessage = null; 
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
