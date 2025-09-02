import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PdfQuizzes } from './pdf-quizzes';

describe('PdfQuizzes', () => {
  let component: PdfQuizzes;
  let fixture: ComponentFixture<PdfQuizzes>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PdfQuizzes]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PdfQuizzes);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
