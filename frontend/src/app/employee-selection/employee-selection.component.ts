import { Component } from '@angular/core';
import { MatDatepicker } from '@angular/material/datepicker';
import * as moment from 'moment';
import { Moment } from 'moment';

@Component({
  selector: 'app-employee-selection',
  templateUrl: './employee-selection.component.html',
  styleUrls: ['./employee-selection.component.scss'],
})
export class EmployeeSelectionComponent {
  employees = [
    { name: 'John Doe', id: 'E001' },
    { name: 'Jane Smith', id: 'E002' },
    // Add more employees...
  ];

  displayedColumns = ['name','inTime','outTime']

  selectedEmployee: any;
  selectedDate: any;
  attendance: any;
  
  todayAttendance:any;

  viewAttendance() {
    // Simulate retrieving attendance based on the selected employee and date
    this.attendance = {
      inTime: '09:00 AM',
      outTime: '05:00 PM',
    };
  }
  
  chosenMonthHandler(normalizedMonth: Moment, datepicker: MatDatepicker<Moment>) {
    const ctrlValue = this.selectedDate || moment();
    ctrlValue.month(normalizedMonth.month());
    ctrlValue.year(normalizedMonth.year());
    this.selectedDate = ctrlValue;
    datepicker.close();
  }
}
