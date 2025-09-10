import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AllQuizzes } from './all-quizzes';

describe('AllQuizzes', () => {
  let component: AllQuizzes;
  let fixture: ComponentFixture<AllQuizzes>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AllQuizzes]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AllQuizzes);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
