import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SingleVideoQuizzes } from './single-video-quizzes';

describe('SingleVideoQuizzes', () => {
  let component: SingleVideoQuizzes;
  let fixture: ComponentFixture<SingleVideoQuizzes>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SingleVideoQuizzes]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SingleVideoQuizzes);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
