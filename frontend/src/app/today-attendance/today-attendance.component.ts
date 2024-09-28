import { Component, OnInit } from '@angular/core';
import { AttendanceService } from '../attendance.service';

@Component({
  selector: 'app-today-attendance',
  templateUrl: './today-attendance.component.html',
  styleUrls: ['./today-attendance.component.scss'],
})
export class TodayAttendanceComponent implements OnInit {
  todayAttendance :any[]=[]

  displayedColumns: string[] = [ 'id' ,'name', 'inTime', 'outTime','status'];

  constructor(private service: AttendanceService) {}
  ngOnInit(): void {
    this.service.getAllTodayAttendance().subscribe({
      next: (res) => {
        this.todayAttendance = res.data;
        console.log(res);
      },
      error: (err) => {
        console.log(err);
      },
    });
  }
}
