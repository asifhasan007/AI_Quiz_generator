import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MultipleVideosQuizzes } from './multiple-videos-quizzes';

describe('MultipleVideosQuizzes', () => {
  let component: MultipleVideosQuizzes;
  let fixture: ComponentFixture<MultipleVideosQuizzes>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MultipleVideosQuizzes]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MultipleVideosQuizzes);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
