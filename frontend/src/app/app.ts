import { Component, signal } from '@angular/core';
import { NavbarComponent } from './navbar/nav';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,              
  imports: [NavbarComponent, CommonModule, RouterOutlet],      
  templateUrl: './app.html',
  styleUrls: ['./app.css']       
})
export class App {
  protected readonly title = signal('quizapp');
}
