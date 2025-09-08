import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class QuizStateService {
  // This array will hold the results across the application
  public generatedItems: { source: string, type: 'video' | 'pdf', quiz: any, error?: string }[] = [];
  
  // This flag will remember if the quiz results table should be shown
  public quizGenerated: boolean = false;

  // ✅ 1. Properly define the property to hold the file
  public lastUploadedFile: File | null = null;

  constructor() { }

  // Method to add new results
  addItems(items: any[]) {
    this.generatedItems = items;
    this.quizGenerated = true;
  }

  // ✅ 2. Add a method to save the uploaded file
  setLastUploadedFile(file: File) {
    this.lastUploadedFile = file;
  }

  // Method to clear the state when starting a new session
  clearState() {
    this.generatedItems = [];
    this.quizGenerated = false;
    // ✅ 3. Ensure the file is also cleared
    this.lastUploadedFile = null; 
  }
}
