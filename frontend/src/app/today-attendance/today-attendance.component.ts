import { Component } from '@angular/core';

@Component({
  selector: 'app-today-attendance',
  templateUrl: './today-attendance.component.html',
  styleUrls: ['./today-attendance.component.scss'],
})
export class TodayAttendanceComponent {
  todayAttendance = [
    { name: 'John Doe', inTime: '09:00 AM', outTime: '05:00 PM' },
    { name: 'Jane Smith', inTime: '09:15 AM', outTime: '05:10 PM' },
    // Add more employee data here...
  ];

  displayedColumns: string[] = ['name', 'inTime', 'outTime'];
}
